# gcode_streamer.py
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class GCodeStreamer(QObject):
    progress = pyqtSignal(int, int)   # (sent_count, total)
    finished = pyqtSignal()
    pausedChanged = pyqtSignal(bool)
    ack = pyqtSignal(int, bytes)      # (line_idx_1based, b"ok"/b"error:.."/b"ALARM:..")
    log = pyqtSignal(bytes)

    def __init__(self, serial_service, parent=None):
        super().__init__(parent)
        self.serial = serial_service
        self.serial.dataReceived.connect(self._on_data)

        self.timer = QTimer(self)
        self.timer.setInterval(30)  # fallback pacing
        self.timer.timeout.connect(self._try_send_next)

        self.lines: list[bytes] = []
        self.idx = 0               # next line to send (0-based)
        self.total = 0
        self.awaiting_ok = False
        self._paused = False

        self._rx = bytearray()     # <-- accumulate until '\n'

    def start(self, lines: list[bytes], wake=True, unlock=False):
        # ensure each line is bytes and newline-terminated on write
        self.lines = [ln.strip() for ln in (lines or []) if ln.strip()]
        self.idx = 0
        self.total = len(self.lines)
        self.awaiting_ok = False
        self._paused = False
        self.pausedChanged.emit(False)
        self._rx.clear()

        if not self.serial.is_open() or not self.lines:
            self.finished.emit()
            return

        if wake:
            self.serial.write(b"\r\n")  # wake GRBL
        if unlock:
            self.serial.write(b"$X\n")  # optional: unlock alarm

        self.timer.start()
        self._try_send_next()

    def stop(self, soft_reset=False):
        self.timer.stop()
        self.lines = []
        self.idx = 0
        self.awaiting_ok = False
        self._paused = False
        self.pausedChanged.emit(False)
        if soft_reset:
            try: self.serial.write(b"\x18")  # Ctrl+X
            except: pass
        self.finished.emit()

    def pause(self):
        self._paused = True
        self.pausedChanged.emit(True)

    def resume(self):
        if not self._paused:
            return
        self._paused = False
        self.pausedChanged.emit(False)
        self._try_send_next()

    def is_paused(self) -> bool:
        return self._paused

    # ----- internals -----
    def _on_data(self, data: bytes):
        # accumulate and process complete lines
        self._rx.extend(data)
        while True:
            nl = self._rx.find(b'\n')
            if nl == -1:
                break
            line = self._rx[:nl].strip()
            del self._rx[:nl+1]
            if not line:
                continue
            low = line.lower()

            # classify responses
            if low == b"ok" or low == b"start":
                self.awaiting_ok = False
                self.ack.emit(self.idx, line)
                self._try_send_next()
            elif low.startswith(b"error:") or low.startswith(b"alarm:"):
                # decide: stop, or pause and let UI decide
                self.awaiting_ok = False
                self.ack.emit(self.idx, line)
                self.stop(soft_reset=False)  # or: self.pause()
            else:
                # status/debug like "<Idle|...>", "$$" dumps, etc.
                self.log.emit(line)

    def _try_send_next(self):
        if self._paused or self.awaiting_ok:
            return
        if self.idx >= self.total:
            self.timer.stop()
            self.finished.emit()
            return

        line = self.lines[self.idx]
        # ensure newline
        payload = line + (b"" if line.endswith(b"\n") else b"\n")
        self.serial.write(payload)

        self.idx += 1
        self.awaiting_ok = True
        self.progress.emit(self.idx, self.total)
