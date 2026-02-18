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
        #idx is the index of the next line to send, tracks how many lines have been sent
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
        print(f"[GCodeStreamer] start(): total={self.total}, is_open={self.serial.is_open()}", flush=True)
        if not self.serial.is_open() or not self.lines:
            print("[GCodeStreamer] start(): early-finish path hit", flush=True)
            self.finished.emit()
            return
        
        self.timer.start()
        print("[GCodeStreamer] start(): timer started, calling _try_send_next()", flush=True)
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
         #print(f"[RX raw] {data!r}", flush=True)

         while True:
            #the find function looks for the first occurrence of b'\n' in the bytearray self._rx, and return -1 if not found 
            nl = self._rx.find(b'\n')
            if nl == -1:
                break
            # Pop one line (tolerate CRLF / LF)
            line = self._rx[:nl+1]
            del self._rx[:nl+1]
            s = line.strip().lower()

            #used for debugging can remove later
            #self.v.log(line.decode('ascii','replace'))

            #removes any strings that are empty after stripping whitespace
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
            #print(f"[GCodeStreamer] _try_send_next(): paused={self._paused}, awaiting_ok={self.awaiting_ok}, returning early", flush=True)
            return
        if self.idx >= self.total:
           # print("[GCodeStreamer] _try_send_next(): all done, stopping timer and emitting finished", flush=True)
            self.timer.stop()
            self.finished.emit()
            return
        line = self.lines[self.idx]
        self.idx += 1
        self.awaiting_ok = True
        print(f"[GCodeStreamer] _try_send_next(): sending line {self.idx}/{self.total}: {line!r}", flush=True)
        self.serial.write(line)
        print(f"[GCodeStreamer] _try_send_next(): line sent, emitting progress", flush=True)
        self.progress.emit(self.idx, self.total)
        print(f"[GCodeStreamer] _try_send_next(): progress emitted", flush=True)