# serial_service.py — threaded pyserial backend (PyQt6, Python 3.13)
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from serial.tools import list_ports
import serial
import time


class _SerialWorker(QObject):
    """Lives in a QThread. Reads bytes and writes on request."""
    bytesReady = pyqtSignal(bytes)   # device -> host
    errorText = pyqtSignal(str)
    closed    = pyqtSignal()

    def __init__(self, ser: serial.Serial):
        super().__init__()
        self._ser = ser
        self._running = False

    @pyqtSlot()
    def run(self) -> None:
        """Reader loop (thread context)."""
        self._running = True
        try:
            while self._running and self._ser and self._ser.is_open:
                try:
                    waiting = self._ser.in_waiting
                    if waiting:
                        chunk = self._ser.read(waiting)
                        if chunk:
                            self.bytesReady.emit(chunk)
                    else:
                        time.sleep(0.01)  # yield CPU
                except Exception as e:
                    self.errorText.emit(f"Serial read error: {e}")
                    break
        finally:
            try:
                if self._ser and self._ser.is_open:
                    self._ser.close()
            except Exception:
                pass
            self.closed.emit()

    @pyqtSlot(bytes)
    def write(self, data: bytes) -> None:
        """Thread-safe write (queued from GUI thread)."""
        try:
            if self._ser and self._ser.is_open:
                #writes data to serial port directory in bytes,could also encode and wrtite
                self._ser.write(data)
        except Exception as e:
            self.errorText.emit(f"Serial write error: {e}")

    @pyqtSlot()
    def stop(self) -> None:
        self._running = False


class SerialService(QObject):
    """
    Threaded pyserial service exposing the same interface/signals as the QtSerialPort version.
      Signals:
        - dataReceived(bytes)
        - errorText(str)
        - connectionChanged(bool, str)   # (connected, "PORT @ BAUD")
      Methods:
        - available_ports() -> list[tuple[str, str]]
        - open(port_path: str, baud: int) -> bool
        - close() -> None
        - is_open() -> bool
        - write(data: bytes) -> int
    """
    dataReceived = pyqtSignal(bytes)
    errorText = pyqtSignal(str)
    connectionChanged = pyqtSignal(bool, str)

    # Internal signal used to queue writes into the worker thread
    writeRequest = pyqtSignal(bytes)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        #the code after the colon is a type hint
        # a type hint is a special comment that tells you what type a variable is
        #it does not affect the code at all
        #it is just for the reader of the code
        self._thread: QThread | None = None
        self._worker: _SerialWorker | None = None
        self._ser: serial.SerialBase | None = None
        self._is_open: bool = False

    # ---------- Public API ----------
    @staticmethod
    # simiarly another type hint here after the arrow for the return type
    def available_ports() -> list[tuple[str, str]]:
        #antoher type hint here for the variable out
        #sets it as an empty list  intially, but it will be a list of tuples of strings
        out: list[tuple[str, str]] = []
        for p in list_ports.comports():
            out.append((f"{p.device}  ({p.description})".strip(), p.device))
        return out

    def open(self, port_path: str, baud: int) -> bool:
        self.close()  # ensure clean state

        try:
            self._ser = serial.Serial(
                port=port_path,
                baudrate=baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1,        # unblocks read loop periodically
                write_timeout=1.0,
            )
        except Exception as e:
            self._ser = None
            self.errorText.emit(f"Open failed: {e}")
            self.connectionChanged.emit(False, "")
            return False

        # Start worker thread
        self._thread = QThread(self)
        self._worker = _SerialWorker(self._ser)
        self._worker.moveToThread(self._thread)

        # Wire signals (cross-thread => queued connections)
        self._thread.started.connect(self._worker.run)
        self._worker.bytesReady.connect(self.dataReceived)
        self._worker.errorText.connect(self.errorText)
        self._worker.closed.connect(self._on_worker_closed)
        self.writeRequest.connect(self._worker.write)

        self._thread.start()
        self._is_open = True
        self.connectionChanged.emit(True, f"{port_path} @ {baud}")

        # Optional: wake some firmwares
        self.write(b"\r\n")
        return True

    def close(self) -> None:
        if not self._is_open:
            # Still ensure resources are cleaned if half-open
            self._cleanup_thread()
            return

        self._is_open = False
        try:
            if self._worker:
                self._worker.stop()     # signal the loop to exit
            if self._thread:
                self._thread.quit()
                self._thread.wait(1000)
        finally:
            self._cleanup_thread()
            self.connectionChanged.emit(False, "")

    def is_open(self) -> bool:
        return self._is_open

    def write(self, data: bytes) -> int:
        if not self._is_open or not self._worker:
            self.errorText.emit("Serial not open.")
            return 0
        # Queue into worker thread
        self.writeRequest.emit(data)
        return len(data)

    # ---------- Internals ----------
    def _on_worker_closed(self) -> None:
        # Worker closed the port (e.g., error). Normalize state.
        if self._is_open:
            self._is_open = False
            self.connectionChanged.emit(False, "")
        self._cleanup_thread()

    def _cleanup_thread(self) -> None:
        # Safely tear down thread/worker/serial
        try:
            if self._thread and self._thread.isRunning():
                self._thread.quit()
                self._thread.wait(500)
        except Exception:
            pass
        try:
            if self._ser and self._ser.is_open:
                self._ser.close()
        except Exception:
            pass
        self._worker = None
        self._thread = None
        self._ser = None
