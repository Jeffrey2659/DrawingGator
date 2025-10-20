# presenter.py
from typing import Optional
from model import GCodeModel
from serial_service import SerialService
from gcode_streamer import GCodeStreamer

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

        # Service -> Presenter
        self.s.dataReceived.connect(self._on_device_data)
        self.s.errorText.connect(self._on_error_text)
        self.s.connectionChanged.connect(self._on_conn_changed)
        self.streamer.progress.connect(self._on_progress)
        self.streamer.finished.connect(self._on_finished)
        self.streamer.pausedChanged.connect(self._on_paused_changed)

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
