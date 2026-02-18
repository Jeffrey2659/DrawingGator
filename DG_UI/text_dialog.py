# text_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QComboBox, QSpinBox, QCheckBox, QDialogButtonBox,
)


class TextDrawDialog(QDialog):
    FONTS = [
        "futural",
        "futuram",
        "rowmans",
        "rowmand",
        "rowmant",
        "scripts",
        "scriptc",
        "cursive",
        "gothiceng",
        "gothicger",
        "gothicita",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Draw Text")
        self.setMinimumWidth(380)

        self.setStyleSheet("""
            QDialog { background-color: #faf5e4; }
            QLabel  { color: #4a4a4a; background-color: transparent; }
            QTextEdit, QComboBox, QSpinBox {
                background-color: #ffffff;
                color: #4a4a4a;
                border: 1px solid #d9c5a0;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton {
                background-color: #f5deb3;
                color: #5a5a5a;
                border: 1px solid #d9c5a0;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #f0d19e; }
            QCheckBox {
                color: #2d5a3d;
                font-weight: bold;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #2d5a3d;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #2d5a3d;
            }
        """)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Text to draw:"))
        self._text_edit = QTextEdit()
        self._text_edit.setPlaceholderText("Type your text here...")
        self._text_edit.setMaximumHeight(120)
        layout.addWidget(self._text_edit)

        row = QHBoxLayout()
        row.addWidget(QLabel("Font:"))
        self._font_combo = QComboBox()
        self._font_combo.addItems(self.FONTS)
        row.addWidget(self._font_combo)

        row.addWidget(QLabel("Size:"))
        self._size_spin = QSpinBox()
        self._size_spin.setRange(6, 200)
        self._size_spin.setValue(18)
        row.addWidget(self._size_spin)
        layout.addLayout(row)

        self._mirror_check = QCheckBox("Mirror horizontally (window backside)")
        layout.addWidget(self._mirror_check)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_text(self) -> str:
        return self._text_edit.toPlainText()

    def get_font(self) -> str:
        return self._font_combo.currentText()

    def get_size(self) -> float:
        return float(self._size_spin.value())

    def get_mirror(self) -> bool:
        return self._mirror_check.isChecked()
