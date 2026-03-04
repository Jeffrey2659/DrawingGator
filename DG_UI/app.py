# app.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from PyQt6.QtWidgets import QApplication
from front_page import FrontPage

def main():
    app = QApplication(sys.argv)
    window = FrontPage()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
