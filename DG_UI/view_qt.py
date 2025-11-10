# view_qt.py
from typing import Optional, List
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QProgressBar, QDockWidget, QWidget, QHBoxLayout, QLineEdit, QPushButton
from DG_UI import Ui_MainWindow
from PyQt6.QtCore import Qt
from matplotlib_widget import MatplotlibWidget
from color_widget import ColorWidget

class ViewQt(QMainWindow, Ui_MainWindow):
    # Presenter assigns these callables at runtime:
    on_refresh_clicked = None
    on_connect_clicked = None
    on_upload_clicked = None
    on_send_clicked = None
    # Optional (add buttons later if desired):
    on_pause_clicked = None
    on_resume_clicked = None
    on_upload_svg = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Drawing Gator")

        #manual command dock
        dock = QDockWidget("Manual Command", self)
        dock.setObjectName("ManualCommandDock")
        dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)


        # add the matplotlib widget for svg display
        self.mpl_widget = MatplotlibWidget()
        preview_dock = QDockWidget("SVG Preview", self)
        preview_dock.setObjectName("SVGPreviewDock")
        preview_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        preview_dock.setWidget(self.mpl_widget)
        preview_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                                  QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                                  QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, preview_dock)
        
        # Set initial size for the dock (optional but helpful)
        preview_dock.setMinimumWidth(300)
        w = QWidget(dock)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)

        self.manualLine = QLineEdit(w)
        self.manualLine.setPlaceholderText("Type a G-code, e.g. G0 X10 Y10 (Enter to send)")
        self.manualSendBtn = QPushButton("Send", w)

        lay.addWidget(self.manualLine, 1)
        lay.addWidget(self.manualSendBtn, 0)

        w.setLayout(lay)
        dock.setWidget(w)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

        # Status progress bar (no .ui changes needed)
        self._progress = QProgressBar(self)
        self._progress.setMinimum(0)
        self._progress.setMaximum(1)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        self.statusbar.addPermanentWidget(self._progress, 1)

        # manual send

        self.on_manual_send = None
        # UI -> Presenter callbacks
        #if no lambda then it calls the function immediately instead of waiting for the button to be clicked
        #the lambda creates an anonymous function that calls the function when the button is clicked
        self.refresh.clicked.connect( lambda: self.on_refresh_clicked and self.on_refresh_clicked())
        self.connect.clicked.connect(lambda: self.on_connect_clicked and self.on_connect_clicked())
        self.sendGcode.clicked.connect(lambda: self.on_send_clicked and self.on_send_clicked())
        self.actionUpload_Gcode.triggered.connect(lambda: self.on_upload_clicked and self.on_upload_clicked())



        # manual present callbacks
        self.manualLine.returnPressed.connect(self._send_manual_from_line)
        self.manualSendBtn.clicked.connect(self._send_manual_from_button)


        #svg upload
        #this is mapped to the uploadImage button rn, I might add a separate button later
        self.actionUpload_Image.triggered.connect(self._ask_open_svg)
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
    def _send_manual_from_line(self):
        txt = self.manualLine.text().strip()
        if txt and self.on_manual_send:
            self.on_manual_send(txt)
            self.manualLine.clear()

    def _send_manual_from_button(self):
        txt = self.manualLine.text().strip()
        if txt and self.on_manual_send:
            self.on_manual_send(txt)
            self.manualLine.clear()
    def _ask_open_svg(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image or SVG", "", "Image or SVG Files (*.svg *.png *.jpg *.jpeg *.bmp))")
        if path and self.on_upload_svg:
            self.on_upload_svg(path)


    def open_color_window(self):
        self.color_window = ColorWidget(self)
        # call the function to display the color on the image
        self.color_window.color_sel.connect(self.mpl_widget.update_colors)
        self.color_window.show()