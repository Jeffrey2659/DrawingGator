# presenter.py
from typing import Optional
from model import GCodeModel
from serial_service import SerialService
from gcode_streamer import GCodeStreamer
from vpype_runner import VpypeRunner
from pathlib import Path

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


        # This checks if the view has an attribute 'on_upload_svg' and if so, assigns the presenter's 'handle_upload_svg' method to it.
        if hasattr(self.v, "on_upload_svg"):
            self.v.on_upload_svg = self.handle_upload_svg

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
        self.s.dataReceived.connect(self._on_rx_log)
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
        for line in data.decode("utf-8", errors="replace").splitlines():
            if line.strip():
                self.v.log(f"<< {line.strip()}")

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

        
    def handle_upload_svg(self, svg_path: str):
        self.v.log(f"Uploaded File: {svg_path}")
        ext = Path(svg_path).suffix.lower()

        # check the extensions of the file loaded
        if ext in [".png", ".jpg", ".jpeg", ".bmp"]:   
            self.v.log("Conversion has started")
            try:
                _,_,_, output_svg = conversion_svg(svg_path)
                svg_path = output_svg
                self.v.log("Yay!")

                # get the animation code
                strokes, num_strokes = extract_coordinates(svg_path)
                self.v.log(f"extracted {len(strokes)}")
                # call the widget to show svg
                if hasattr(self.v, 'mpl_widget'):
                    self.v.mpl_widget.plot_svg(strokes)

                #animation_simulation(strokes)
                #display_svg(strokes)
            except Exception as e:
                self.v.warn(f"SVG conversion failed: {e}")
                return
        # Now convert the SVG to G-code using vpype
        self.v.log("Starting vpype conversion to G-code…")
        out_path = str(Path(svg_path).with_suffix(".gcode"))
        self.v.log(f"G-code will be saved to: {Path(out_path).resolve()}")
        self._vp.run_svg_to_gcode(svg_path, out_path=out_path)
                                 
        '''
        self.v.log(f"Converting with vpype: {svg_path}\n")
        # Decide output .gcode location (temp is fine)
        out_path = str(Path(svg_path).with_suffix(".gcode"))
        # Tune these to your machine (or store in settings)
        self._vp.run_svg_to_gcode(svg_path,
                                  out_path=out_path
                                 )
        #extra paramters to addd later  pen_up_z=5.0,
                                 # pen_down_z=0.0,
                                 # feed=2000
'''

     #  when vpype finishes, load the file into the model
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