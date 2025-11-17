# presenter.py
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from typing import Optional
from model import GCodeModel
from serial_service import SerialService
from gcode_streamer import GCodeStreamer
from vpype_runner import VpypeRunner
from pathlib import Path
import serial
import os


# load the algorithm and all its functions
from Interface.svg_algorithm import conversion_svg, extract_coordinates, animation_simulation, display_svg

class Presenter:
    """
    The Presenter expects the 'view' to provide:
      - set_ports(List[str]), set_connected(bool, str), set_progress(int,int)
      - log(str), warn(str), ask_open_file()->Optional[str]
      - current_port()->str, current_baud()->int
      - callables: on_refresh_clicked, on_connect_clicked, on_upload_clicked, on_send_clicked
        (optional: on_pause_clicked, on_resume_clicked)
    """
    def __init__(self, view, serial_service: SerialService, model: GCodeModel):
        self.v = view
        self.s = serial_service
        self.m = model
        self.streamer = GCodeStreamer(self.s)
        self._state_block_active = False
        self._state_lines: list[str] = []
        self._rx_buffer = ""


        # This checks if the view has an attribute 'on_upload_svg' and if so, assigns the presenter's 'handle_upload_svg' method to it.
        if hasattr(self.v, "on_upload_svg"):
            self.v.on_upload_svg = self.handle_upload_svg

        #for general image upload
        # self.v.on_upload_image = self._on_upload_image
        self._vp = VpypeRunner()
        self._vp.finished.connect(self._on_vpype_finished)

        # Service -> Presenter
        self.s.dataReceived.connect(self._on_device_data)
        self.s.errorText.connect(self._on_error_text)
        self.s.connectionChanged.connect(self._on_conn_changed)
        self.streamer.progress.connect(self._on_progress)
        self.streamer.finished.connect(self._on_finished)
        self.streamer.pausedChanged.connect(self._on_paused_changed)

        #used for logging received data from the device
        #self.s.dataReceived.connect(self._on_rx_log)
        #used for debugging raw received data
        self.s.dataReceived.connect(lambda b: print(f"[RX RAW] {b!r}", flush=True))
        #manual send
        self.v.on_manual_send = self.handle_manual_send
        
        # View -> Presenter
        self.v.on_refresh_clicked = self.handle_refresh
        self.v.on_connect_clicked = self.handle_connect_toggle
        self.v.on_upload_clicked  = self.handle_upload
        self.v.on_send_clicked    = self.handle_send
        if hasattr(self.v, "on_pause_clicked"):
            self.v.on_pause_clicked = self.handle_pause
        if hasattr(self.v, "on_resume_clicked"):
            self.v.on_resume_clicked = self.handle_resume

    def start(self):
        self.handle_refresh()
        self.v.log("Ready. Upload G-code, choose a port, Connect, then Send.")

    # ---- View handlers ----
    def handle_refresh(self):
        ports = [lbl for (lbl, _) in self.s.available_ports()]
        self.v.set_ports(ports)
        if not ports:
            self.v.log("No serial ports found. Plug in your board and click Refresh.")

    def handle_connect_toggle(self):
        if self.s.is_open():
            self.s.close()
            return
        port_label = self.v.current_port().strip()
        if not port_label:
            self.v.warn("Select a port first.")
            return
        port_path = port_label.split()[0]  # "/dev/ttyACM0" or "COM3"
        baud = self.v.current_baud()
        if baud == 1115200:  # typo guard
            baud = 115200
        if not self.s.open(port_path, baud):
            self.v.warn("Failed to open port.")

    def handle_upload(self):
        #ask_open_file is a function of the view that opens a file dialog and returns the selected file path or None
        path: Optional[str] = self.v.ask_open_file()
        if not path:
            return
        try:
            #call the load_from_file function of the model to load the gcode file and parse it
            n = self.m.load_from_file(path)
            self.v.set_progress(0, max(1, self.m.total))
            self.v.log(f"Loaded {n} lines from {self.m.loaded_name}")
            joined = "\n".join(line.decode("ascii", errors="ignore") for line in self.m.lines)
            self.v.log("=== Loaded G-code ===\n" + joined)
        except Exception as e:
            self.v.warn(f"Could not read file:\n{e}")

    def handle_send(self):
        if not self.s.is_open():
            self.v.warn("Not connected.")
            return
        if not self.m.lines:
            self.v.warn("No G-code loaded.")
            return
        self.m.reset_job_counters()
        self.v.log("Starting G-code stream…")
        for raw in self.m.lines:
            try:
                line = raw.decode("ascii", errors="replace").rstrip()
            except Exception:
                line = repr(raw)
            if line:
                self.v.log(f">> {line}")
        self.streamer.start(self.m.lines)
        self.v.log("Streaming started: Debug Checkpoint 1.")

    def handle_pause(self):
        if not self.streamer.is_paused():
            self.streamer.pause()
            self.v.log("Paused.")

    def handle_resume(self):
        if self.streamer.is_paused():
            self.v.log("Resuming…")
            self.streamer.resume()

    # ---- Service callbacks ----
    def _on_device_data(self, data: bytes):
        # 1) Decode and normalize newlines
        text = data.decode("utf-8", errors="replace")
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # 2) Append to rolling buffer
        self._rx_buffer += text

        # 3) Extract complete lines one by one
        while True:
            nl = self._rx_buffer.find("\n")
            if nl == -1:
                # No full line yet; leave remainder for next chunk
                break

            raw_line = self._rx_buffer[:nl]
            self._rx_buffer = self._rx_buffer[nl+1:]  # remove that line + '\n'

            line = raw_line.strip()
            if not line:
                continue

            # Hand off to line-level handler
            self._handle_rx_line(line)


    def _handle_rx_line(self, line: str):
        """Process a single complete line from the controller."""
        # State-dump logic (G60 etc.) still works unchanged
        if line.startswith("Printing State:"):
            self._state_block_active = True
            self._state_lines = [line]
            return

        if self._state_block_active:
            self._state_lines.append(line)
            if line.startswith("End of States"):
                block = "\n".join("<< " + l for l in self._state_lines)
                self.v.log(block)
                self._state_block_active = False
                self._state_lines = []
            return

        # Normal line
        self.v.log(f"<< {line}")

    def _on_error_text(self, text: str):
        self.v.warn(text)

    def _on_conn_changed(self, ok: bool, desc: str):
        self.v.set_connected(ok, desc)
        self.v.log(f"{'Connected: ' + desc if ok else 'Disconnected.'}")

    def _on_progress(self, sent: int, total: int):
        self.m.sent = sent
        self.v.set_progress(sent, total)
        self.v.log(f">> [{sent}/{total}]")

    def _on_finished(self):
        self.v.set_progress(self.m.total, max(1, self.m.total))
        self.v.log("Stream complete.")

    def _on_paused_changed(self, paused: bool):
        # Hook for toggling UI when you add Pause/Resume buttons
        pass
    def handle_manual_send(self, text: str):
        print(f"[manual] got: {text!r}", flush=True)
        if not self.s.is_open():
            self.v.warn("Not connected to a device.")
            return
        # GRBL expects CRLF; ensure it’s appended exactly once
        cmd = text.strip()
        if not cmd:
            return
        if not cmd.endswith("\r") and not cmd.endswith("\n"):
            cmd += "\r\n"
        elif cmd.endswith("\n") and not cmd.endswith("\r\n"):
            # normalize lone LF to CRLF
            cmd = cmd[:-1] + "\r\n"

        self.v.log(f">> {text}")  # echo to log pane
        try:
            n =  self.s.write(cmd.encode("ascii", errors="ignore"))
            print(f"[manual] queued {n} bytes", flush=True)
        except Exception as e:
            self.v.warn(f"Send failed: {e}")

    def _on_rx_log(self, data: bytes):
        """Low-level logger for all serial RX data (GRBL responses)."""
        try:
            text = data.decode("ascii", errors="replace")
        except Exception:
            text = repr(data)
        # Normalize newlines for clean display
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        self.v.log(text)

    def ask_open_svg_file(self) -> Optional[str]:
        if hasattr(self.v, 'ask_open_file_with_dir'):
            return self.v.ask_open_file_with_dir(
                self.default_image_dir,
                "Image Files (*.svg *.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
            )
        
        # Fallback: use standard ask_open_file
        return self.v.ask_open_file()

        
    def handle_upload_svg(self, svg_path: str = None):
        if svg_path is None:
            svg_path = self.ask_open_svg_file()
            if not svg_path:
                return

        svg_path = str(svg_path)
        if not Path(svg_path).exists():
            self.v.warn(f"file not found: {svg_path}")
            return

        self.v.log(f"Uploaded File: {svg_path}")
        ext = Path(svg_path).suffix.lower()

        # ------------------ PREVIEW SECTION ------------------
        try:
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                # 1) Raster → SVG
                self.v.log("Conversion has started")
                # adjust return values to match your actual conversion_svg version
                lines, width, height, width_inch, height_inch, width_cm, height_cm, output_svg = conversion_svg(svg_path)
                svg_path = output_svg  # now work with the generated SVG
                self.v.log("Yay! Raster image converted to SVG.")

                # 2) Extract strokes from the new SVG and preview
                strokes,num_strokes = extract_coordinates(svg_path)
                self.v.log(f"Extracted {num_strokes} strokes from converted SVG")

                if hasattr(self.v, "mpl_widget"):
                    self.v.mpl_widget.plot_svg(strokes,num_strokes=num_strokes, image_size=(width_inch, height_inch))

            elif ext == ".svg":
                # Already an SVG: just extract coordinates and preview
                self.v.log("SVG file detected. Skipping raster conversion.")
                strokes, num_strokes = extract_coordinates(svg_path)
                self.v.log(f"Extracted {num_strokes} strokes from SVG")

                if hasattr(self.v, "mpl_widget"):
                    # We may not know the physical size, so just omit image_size
                    self.v.mpl_widget.plot_svg(strokes,num_strokes=num_strokes)
            else:
                self.v.warn(f"Unsupported file type for preview: {ext}")
        except Exception as e:
            self.v.warn(f"SVG preview failed: {e}")
            # we still continue to vpype below, since G-code generation might work

        # ------------------ VTYPE → G-CODE SECTION ------------------
        self.v.log("Starting vpype conversion to G-code…")
        out_path = str(Path(svg_path).with_suffix(".gcode"))
        self.v.log(f"G-code will be saved to: {Path(out_path).resolve()}")
        self._vp.run_svg_to_gcode(svg_path, out_path=out_path)
    def _on_vpype_finished(self, ok: bool, gcode_path: str, log_text: str):
        if log_text:
            self.v.log(log_text + ("\n" if not log_text.endswith("\n") else ""))
        if not ok:
            self.v.warn("vpype conversion failed.")
            return
        try:
            count = self.m.load_from_file(gcode_path)
            self.v.log(f"Loaded {count} lines from {gcode_path}\n")
            # Optionally show a quick preview/progress reset if your View has it
            if hasattr(self.v, "set_progress"):
                self.v.set_progress(0, max(count, 1))
        except Exception as e:
            self.v.warn(f"Failed to load G-code: {e}")
    def _on_upload_image(self, img_path: str):
        """1) Raster → SVG (potrace), then kick off vpype."""
        self.v.log(f"Image selected: {img_path}")
        # Choose output beside image
        svg_out = str(Path(img_path).with_suffix(".svg"))

        #Need to change this to be robust
        #CHANGE THIS 
    

        # Run in a worker thread so the UI stays responsive
        t = QThread(self.v)
        class _Worker(QObject):
            done = pyqtSignal(object, object)  # (err, svg_path)
            def run(self_nonlocal):
                try:
                    # conversion_svg will raise if potrace not found/returns nonzero
                    #do not need to add potrace path here as it is added in the function, witht the find_potrace function
                    _, _, _, svg_path = conversion_svg(img_path, svg_out)
                    self_nonlocal.done.emit(None, svg_path)
                except Exception as e:
                    self_nonlocal.done.emit(e, None)

        w = _Worker()
        w.moveToThread(t)
        t.started.connect(w.run)
        w.done.connect(lambda err, svg: self._after_svg(err, svg, t, w))
        t.start()
    def _after_svg(self, err, svg_path, t, w):
        t.quit(); t.wait()
        # (Let GC collect w/t)
        if err:
            self.v.warn(f"SVG conversion failed: {err}")
            return
        self.v.log(f"SVG created: {svg_path}")
        # 2) SVG → G-code via vpype
        gcode_out = str(Path(svg_path).with_suffix(".gcode"))
        self._vp.run_svg_to_gcode(svg_path, gcode_out)
