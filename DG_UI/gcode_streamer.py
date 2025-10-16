# gcode_streamer.py
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

OK_TOKENS = (b"ok", b"start")  # tweak for your firmware
TERM_TOKENS = (b"ok", b"error:", b"alarm:", b"start")  # new
class GCodeStreamer(QObject):
    progress = pyqtSignal(int, int)  # (sent, total)
    finished = pyqtSignal()
    pausedChanged = pyqtSignal(bool)

    def __init__(self, serial_service, parent=None):
        super().__init__(parent)
        self.serial = serial_service
        self.serial.dataReceived.connect(self._on_data)

        self.timer = QTimer(self)
        self.timer.setInterval(30)  # ms fallback pacing
        self.timer.timeout.connect(self._try_send_next)

        self.lines: list[bytes] = []
        self.idx = 0
        self.total = 0
        self.awaiting_ok = False
        self._paused = False

        self._rx = bytearray()


    def start(self, lines: list[bytes]):
        self.lines = lines or []
        self.idx = 0
        self.total = len(self.lines)
        self.awaiting_ok = False
        self._paused = False
        self._rx.clear()
        self.pausedChanged.emit(False)
        if not self.serial.is_open() or not self.lines:
            self.finished.emit()
            return
        self.timer.start()
        self._try_send_next()

    def stop(self):
        self.timer.stop()
        self.lines = []
        self.idx = 0
        self.awaiting_ok = False
        self._paused = False
        self._rx.clear()
        self.pausedChanged.emit(False)

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
         self._rx.extend(data)
         while True:
            nl = self._rx.find(b'\n')
            if nl == -1:
                break
            # Pop one line (tolerate CRLF / LF)
            line = self._rx[:nl+1]
            del self._rx[:nl+1]
            s = line.strip().lower()

            if not s:
                continue

            # Treat any terminal response as an acknowledgment for pacing
            if any(s.startswith(tok) for tok in TERM_TOKENS):
                # You may want to stop-on-error instead of continue; for now we advance.
                self.awaiting_ok = False
                self._try_send_next()
                # Optionally: if s startswith b"error:" or b"alarm:", you could pause/stop and lo

    def _try_send_next(self):
        if self._paused or self.awaiting_ok:
            return
        if self.idx >= self.total:
            self.timer.stop()
            self.finished.emit()
            return
        line = self.lines[self.idx]
        self.idx += 1
        self.awaiting_ok = True
        self.serial.write(line)
        self.progress.emit(self.idx, self.total)
