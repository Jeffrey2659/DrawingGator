# serial_service.py
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo

class SerialService(QObject):
    dataReceived = pyqtSignal(bytes)           # device -> host
    errorText = pyqtSignal(str)
    connectionChanged = pyqtSignal(bool, str)  # (connected, "port @ baud")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ser = QSerialPort(self)
        self._ser.readyRead.connect(self._on_ready_read)
        self._ser.errorOccurred.connect(self._on_error)

    @staticmethod
    def available_ports():
        out = []
        for info in QSerialPortInfo.availablePorts():
            label = f"{info.systemLocation()}  ({info.description()})".strip()
            out.append((label, info.systemLocation()))
        return out

    def open(self, port_path: str, baud: int) -> bool:
        if self._ser.isOpen():
            self.close()
        self._ser.setPortName(port_path)
        self._ser.setBaudRate(baud)
        self._ser.setDataBits(QSerialPort.DataBits.Data8)
        self._ser.setParity(QSerialPort.Parity.NoParity)
        self._ser.setStopBits(QSerialPort.StopBits.OneStop)
        self._ser.setFlowControl(QSerialPort.FlowControl.NoFlowControl)
        ok = self._ser.open(QSerialPort.OpenModeFlag.ReadWrite)
        self.connectionChanged.emit(ok, f"{port_path} @ {baud}" if ok else "")
        if ok:
            self.write(b"\r\n")  # wake some firmwares
        return ok

    def close(self):
        if self._ser.isOpen():
            self._ser.close()
        self.connectionChanged.emit(False, "")

    def is_open(self) -> bool:
        return self._ser.isOpen()

    def write(self, data: bytes) -> int:
        if not self._ser.isOpen():
            self.errorText.emit("Serial not open.")
            return 0
        return self._ser.write(data)

    # ----- internal slots -----
    def _on_ready_read(self):
        data = self._ser.readAll().data()
        if data:
            self.dataReceived.emit(data)

    def _on_error(self, _):
        if self._ser.error():
            self.errorText.emit(self._ser.errorString())
