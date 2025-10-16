# view_qt.py
from typing import Optional, List
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QProgressBar
from DG_UI import Ui_MainWindow

class ViewQt(QMainWindow, Ui_MainWindow):
    # Presenter assigns these callables at runtime:
    on_refresh_clicked = None
    on_connect_clicked = None
    on_upload_clicked = None
    on_send_clicked = None
    # Optional (add buttons later if desired):
    on_pause_clicked = None
    on_resume_clicked = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Drawing Gator")

        # Status progress bar (no .ui changes needed)
        self._progress = QProgressBar(self)
        self._progress.setMinimum(0)
        self._progress.setMaximum(1)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        self.statusbar.addPermanentWidget(self._progress, 1)

        # UI -> Presenter callbacks
        self.refresh.clicked.connect( lambda: self.on_refresh_clicked and self.on_refresh_clicked())
        self.connect.clicked.connect(lambda: self.on_connect_clicked and self.on_connect_clicked())
        self.sendGcode.clicked.connect(lambda: self.on_send_clicked and self.on_send_clicked())
        self.actionUpload_Gcode.triggered.connect(lambda: self.on_upload_clicked and self.on_upload_clicked())

        # If you add Pause/Resume buttons in .ui (names: pauseBtn/resumeBtn), hook them:
        # self.pauseBtn.clicked.connect(lambda: self.on_pause_clicked and self.on_pause_clicked())
        # self.resumeBtn.clicked.connect(lambda: self.on_resume_clicked and self.on_resume_clicked())

    # Presenter -> View API
    def set_ports(self, ports: List[str]) -> None:
        self.portOpt.clear()
        for p in ports:
            self.portOpt.addItem(p)

    def set_connected(self, connected: bool, desc: str = "") -> None:
        self.connect.setText("Disconnect" if connected else "Connect")
        self.statusbar.showMessage(desc if connected else "Disconnected", 3000)

    def set_progress(self, sent: int, total: int) -> None:
        total = max(1, total)
        self._progress.setMaximum(total)
        self._progress.setValue(sent)
        self._progress.setFormat(f"{sent}/{total}")

    def log(self, text: str) -> None:
        self.plainTextEdit.appendPlainText(text)

    def warn(self, text: str) -> None:
        self.statusbar.showMessage(text, 5000)
        QMessageBox.warning(self, "Notice", text)

    def ask_open_file(self) -> Optional[str]:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select G-code file", "",
            "G-code Files (*.gcode *.nc *.ngc *.gco *.txt);;All Files (*)"
        )
        return path or None

    def current_port(self) -> str:
        return self.portOpt.currentText().strip()

    def current_baud(self) -> int:
        txt = self.baudOpt.currentText().strip()
        try:
            return int(txt)
        except ValueError:
            return 115200
