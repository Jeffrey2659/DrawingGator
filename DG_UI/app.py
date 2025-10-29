# app.py
import sys
from PyQt6.QtWidgets import QApplication
from view_qt import ViewQt
from presenter import Presenter
from serial_service import SerialService
from model import GCodeModel

def main():
    app = QApplication(sys.argv)
    view = ViewQt()
    serial = SerialService()
    model = GCodeModel()
    presenter = Presenter(view, serial, model)
    presenter.start()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
