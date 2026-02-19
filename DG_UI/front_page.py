from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QSize
import subprocess
import sys

# app.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from PyQt6.QtWidgets import QApplication
from view_qt import ViewQt
from presenter import Presenter
from serial_service import SerialService
from model import GCodeModel

# REFERENCE: https://stackoverflow.com/questions/58248659/how-to-animate-a-qpushbutton-backgrounds-gradient-to-go-from-left-to-right-on-h
class FrontPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Gator")

        self.setGeometry(100, 100, 800, 600)
        central = QWidget()
        self.setCentralWidget(central)

        # set color
        # working on a mixing of light blue to light orange maybe
        self.setStyleSheet("background-color: qlineargradient(" \
        "spread:pad, x1:0, y1:0, x2:1, y2:1, " \
        "stop:0 rgb(166,231,255), " \
        "stop:1 rgb(255,204,153));")
        
        ## TITLE LAYOUT
        title = QVBoxLayout()
        ## TITLE
        label = QLabel("Drawing")
        # set font and size
        # https://doc.qt.io/qtforpython-6/PySide6/QtGui/QFont.html#PySide6.QtGui.QFont
        label.setFont(QFont("Goudy Stout", 37, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # set color
        label.setStyleSheet("color: rgb(47, 79, 79); background-color: transparent;")

        # all the second part
        sec_part = QHBoxLayout()
        sec_part.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sec_part.setSpacing(0)

        # second part of title
        label2 = QLabel("Gat")
        label2.setFont(QFont("Goudy Stout", 37, QFont.Weight.Bold))
        label2.setStyleSheet("color: rgb(47, 79, 79); background-color: transparent;")

        # logo part instead of O
        logo = QLabel()
        logo.setStyleSheet("background-color: transparent; border: none;")
        image = QPixmap("logo.png")
        logo.setPixmap(image.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))

        # letter r
        label3 = QLabel("r")
        label3.setFont(QFont("Goudy Stout", 37, QFont.Weight.Bold))
        label3.setStyleSheet("color: rgb(47, 79, 79); background-color: transparent;")


        # add all together
        sec_part.addWidget(label2)
        sec_part.addWidget(logo)
        sec_part.addWidget(label3)

        title.addWidget(label)
        title.addLayout(sec_part)

        ## BUTTON
        # set push button to start the app
        button = QPushButton("Feed the Gator")
        button.setFixedSize(200, 50)
        self.button = button
        # button clicked
        self.button.clicked.connect(self.gator_click)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #100c08;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-family: "Berlin Sans FB";
                font-size: 23px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        layout.addStretch() 
        layout.addLayout(title)
        layout.addSpacing(20)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        central.setLayout(layout)
        self.show()

    def gator_click(self):
        # added code from app.py to connect the two
        self.view = ViewQt()
        serial = SerialService()
        model = GCodeModel()
        presenter = Presenter(self.view, serial, model)
        presenter.start()
        self.view.show()
        self.close()
        print("button clicked")

if __name__ == '__main__':
   app = QApplication(sys.argv)
   window = FrontPage()
   sys.exit(app.exec())