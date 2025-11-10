from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QColorDialog, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class ColorWidget(QWidget):
    # Signal emitted when color changes
    color_sel = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None, Qt.WindowType.Window)
        self.current_color = '#000000'

        # Window setup
        self.setWindowTitle('Colors of markers')
        self.setFixedSize(300, 250)
        self.setStyleSheet("background-color: #faf5e4;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Choose a Color")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #4a4a4a; font-size: 14px;")
        layout.addWidget(title)

        # marker colors for the ones we have
        colors = ["#000000", "#FF0000", "#00FF00", "#0000FF", "#800080"]
        color_layout = QHBoxLayout()

        for markers in colors:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {markers}; border-radius: 4px; border: 1px solid #333;")
            btn.clicked.connect(lambda _, col=markers: self.set_color(col))
            color_layout.addWidget(btn)

        layout.addLayout(color_layout)

        self.setLayout(layout)

    def set_color(self, color_str: str):
        self.current_color = color_str
        self.color_sel.emit(color_str)
