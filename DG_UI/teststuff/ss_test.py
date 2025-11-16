# ss_thread_test.py  (Python 3.13)
from PyQt6.QtCore import QCoreApplication, QTimer
import sys

from serial_service import SerialService  # your threaded version

def main():
    app = QCoreApplication(sys.argv)

    svc = SerialService()

    # Observe signals
    svc.dataReceived.connect(lambda b: print("RX:", b))
    svc.errorText.connect(lambda s: print("ERR:", s))
    svc.connectionChanged.connect(lambda ok, info: print("CONN:", ok, info))

    # Open virtual loopback. Requires open() to use serial.serial_for_url(...)
    if not svc.open("loop://", 115200):
        print("Failed to open loop://")
        sys.exit(1)

    # Send a few messages (they should echo back via dataReceived)
    def send_stuff():
        svc.write(b"hello\n")
        svc.write(b"G0 X10 Y20\n")
        svc.write(b"M114\n")

    # Close and exit after a short demo
    def shutdown():
        svc.close()
        app.quit()

    QTimer.singleShot(50, send_stuff)
    QTimer.singleShot(500, shutdown)

    app.exec()

if __name__ == "__main__":
    main()
