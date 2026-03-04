# view_qt.py
from typing import Optional
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QProgressBar, QDockWidget, QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtGui import QAction
from typing import Optional, List
from PyQt6.QtWidgets import QCheckBox, QMainWindow, QFileDialog, QMessageBox, QProgressBar, QDockWidget, QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtGui import QBrush, QColor, QFont, QPaintEvent, QPainter, QPen
from DG_UI import Ui_MainWindow
from PyQt6.QtCore import QPoint, QPointF, QRectF, QSize, Qt
from matplotlib_widget import MatplotlibWidget
from color_widget import ColorWidget
from text_dialog import TextDrawDialog
from pathlib import Path
from PyQt6.QtCore import Qt, QPointF, QRectF, QSize, QPoint, pyqtSlot as Slot, pyqtProperty as Property

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
    on_upload_image = None
    on_draw_text = None

    # Add additional line for svg preview revert
    on_show_svg_preview = None
    on_speed_preset = None


    on_color_clicked = None
    on_grayscale_clicked = None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        ### ADDING DIRECTORY PATH TO IMAGES SO THAT OPENS WHEN UPLOAD FILE IS SELECTED
        self.default_image_dir = Path(__file__).parent.parent / "Interface" / "images"

        #################################################################################
        ############# CHANGING THE COLOR FOR THE WINDOW AND ALL THE BUTTONS #############
        #################################################################################

        ##################################################################################
        ############# ALL CHANGES SHOULD BE MADE HERE FOR THE WINDOW DISPLAY #############
        ##################################################################################

        self.setStyleSheet("""
        /* Main Window Background */
        QMainWindow {
            background-color: #faf5e4;
        }
        
        /* Central Widget */
        QWidget {
            background-color: #faf5e4;
            color: #4a4a4a;
        }
        
        QPushButton {
            background-color: #f5deb3;
            color: #5a5a5a;
            border: 1px solid #d9c5a0;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #f0d19e;
            border: 1px solid #c9b590;
        }
        
        QPushButton:pressed {
            background-color: #e5c68d;
        }
        
        QPushButton#Color {
            background-color: #a8d5ba;
            color: #2d5a3d;
        }
        
        QPushButton#Color:hover {
            background-color: #98c5aa;
        }
        
        QComboBox {
            background-color: #ffffff;
            color: #4a4a4a;
            border: 1px solid #d9c5a0;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox:hover {
            border: 1px solid #c9b590;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid #5a5a5a;
            margin-right: 5px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #4a4a4a;
            selection-background-color: #f5deb3;
            border: 1px solid #d9c5a0;
        }
        
        QLabel {
            color: #4a4a4a;
            background-color: transparent;
        }
        
        QPlainTextEdit, QTextEdit {
            background-color: #ffffff;
            color: #4a4a4a;
            border: 1px solid #d9c5a0;
            border-radius: 4px;
        }
        
        QLineEdit {
            background-color: #ffffff;
            color: #4a4a4a;
            border: 1px solid #d9c5a0;
            border-radius: 4px;
            padding: 4px;
        }
        
        QLineEdit:focus {
            border: 2px solid #f5deb3;
        }
                           
        QMenuBar {
            background-color: #faf5e4;
            color: #4a4a4a;
        }
        
        QMenuBar::item:selected {
            background-color: #f5deb3;
        }
        
        QMenu {
            background-color: #faf5e4;
            color: #4a4a4a;
        }
        
        QMenu::item:selected {
            background-color: #f5deb3;
        }
        
        QStatusBar {
            background-color: #faf5e4;
            color: #4a4a4a;
        }
        
        QProgressBar {
            background-color: #ffffff;
            color: #4a4a4a;
            border: 1px solid #d9c5a0;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #f5deb3;
            border-radius: 3px;
        }
        
        QDockWidget {
            color: #4a4a4a;
        }
        
        QDockWidget::title {
            background-color: #f5deb3;
            text-align: left;
            padding-left: 5px;
            padding-top: 4px;
            padding-bottom: 4px;
            border: 1px solid #d9c5a0;
        }
        """)
        #################################################################################
        #################################################################################

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

        # Speed preset buttons
        speed_container = QWidget(self.centralwidget)
        speed_layout = QHBoxLayout(speed_container)
        speed_layout.setContentsMargins(8, 4, 8, 4)
        speed_layout.addWidget(QLabel("Draw Speed:"))

        self._btn_slow   = QPushButton("Slow\n(50 q-in/min)",   speed_container)
        self._btn_normal = QPushButton("Normal\n(100 q-in/min)", speed_container)
        self._btn_fast   = QPushButton("Fast\n(200 q-in/min)",  speed_container)

        for btn in (self._btn_slow, self._btn_normal, self._btn_fast):
            speed_layout.addWidget(btn)

        self._speed_buttons = {
            "slow":   self._btn_slow,
            "normal": self._btn_normal,
            "fast":   self._btn_fast,
        }

        # Insert before plainTextEdit in the central layout
        idx = self.verticalLayout_2.indexOf(self.plainTextEdit)
        self.verticalLayout_2.insertWidget(idx, speed_container)

        # Wire up clicks
        self._btn_slow.clicked.connect(lambda: self._on_speed_btn("slow"))
        self._btn_normal.clicked.connect(lambda: self._on_speed_btn("normal"))
        self._btn_fast.clicked.connect(lambda: self._on_speed_btn("fast"))

        # Highlight normal as the default
        self._highlight_speed_btn("normal")

        # Status progress bar (no .ui changes needed)
        self._progress = QProgressBar(self)
        self._progress.setMinimum(0)
        self._progress.setMaximum(1)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        self.statusbar.addPermanentWidget(self._progress, 1)

        # toggle 
        self.toggle_switch = ColorSwitch(
            checked_color="#00B0FF",
            h_scale=1.2,
            v_scale=1.2,
        )
        self.statusbar.addWidget(self.toggle_switch)
        self.toggle_switch.toggled.connect(self._on_color_clicked)

        # manual send

        self.on_manual_send = None
        # UI -> Presenter callbacks
        #if no lambda then it calls the function immediately instead of waiting for the button to be clicked
        #the lambda creates an anonymous function that calls the function when the button is clicked
        self.connect.clicked.connect(lambda: self.on_connect_clicked and self.on_connect_clicked())
        self.sendGcode.clicked.connect(lambda: self.on_send_clicked and self.on_send_clicked())
        self.actionUpload_Gcode.triggered.connect(lambda: self.on_upload_clicked and self.on_upload_clicked())



        # manual present callbacks
        self.manualLine.returnPressed.connect(self._send_manual_from_line)
        self.manualSendBtn.clicked.connect(self._send_manual_from_button)


        #svg upload
        #this is mapped to the uploadImage button rn, I might add a separate button later
        self.actionUpload_Image.triggered.connect(self._ask_open_svg)

        # Draw Text menu action
        self.actionDraw_Text = QAction("Draw Text", self)
        self.menuMenu.addAction(self.actionDraw_Text)
        self.actionDraw_Text.triggered.connect(self._ask_draw_text)
        # If you add Pause/Resume buttons in .ui (names: pauseBtn/resumeBtn), hook them:
        # self.pauseBtn.clicked.connect(lambda: self.on_pause_clicked and self.on_pause_clicked())
        # self.resumeBtn.clicked.connect(lambda: self.on_resume_clicked and self.on_resume_clicked())
        #self.actionUpload_Image.triggered.connect(self._ask_open_image)    # Presenter -> View API
        self.colorButton.hide()
        self.create_show_svg_preview()
        

    def _on_color_clicked(self, checked: bool):
            if checked:
                if self.on_color_clicked:
                    self.on_color_clicked()
            else:
                if self.on_grayscale_clicked:
                    self.on_grayscale_clicked()

    def set_connected(self, connected: bool, desc: str = "") -> None:
        self.connect.setText("Disconnect" if connected else "Connect to Arduino")
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
        # ADDINF THE PATH
        if self.default_image_dir.exists():
            init_dir = str(self.default_image_dir)
        else:
            init_dir = ""
            self.warn(f"Folder not found")

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            init_dir,
            "Image or SVG File (*.svg *.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if path and self.on_upload_svg:
            self.on_upload_svg(path)


    def _ask_draw_text(self):
        dlg = TextDrawDialog(self)
        if dlg.exec() == TextDrawDialog.DialogCode.Accepted:
            text = dlg.get_text()
            if text.strip() and self.on_draw_text:
                self.on_draw_text(text, dlg.get_font(), dlg.get_size(), dlg.get_mirror())

    def open_color_window(self):
        self.color_window = ColorWidget(self)
        # call the function to display the color on the image
        self.color_window.color_sel.connect(self.mpl_widget.update_colors)
        self.color_window.show()

    # adding function to bring back svg preview if closed
    def create_show_svg_preview(self):
        view_menu = None
        for action in self.menuBar().actions():
            if action.text() == "View":
                view_menu = action.menu()
                break
        if view_menu is None:
            view_menu = self.menuBar().addMenu("View")
        
        self.preview_dock = self.findChild(QDockWidget, "SVGPreviewDock")
        show_preview_action = view_menu.addAction("Show SVG Preview")
        show_preview_action.triggered.connect(self.show_preview)

    # reselect svg preview if closed
    def show_preview(self):
        if self.preview_dock.isHidden():
            self.preview_dock.show()
        self.preview_dock.raise_()
        self.preview_dock.activateWindow()

    def _on_speed_btn(self, preset: str):
        self._highlight_speed_btn(preset)
        if self.on_speed_preset:
            self.on_speed_preset(preset)

    def _highlight_speed_btn(self, preset: str):
        active_style = (
            "background-color: #a8d5ba; color: #2d5a3d;"
            "border: 2px solid #2d5a3d; border-radius: 4px;"
            "padding: 6px 12px; font-weight: bold;"
        )
        for name, btn in self._speed_buttons.items():
            btn.setStyleSheet(active_style if name == preset else "")
# class for color switch
# References: https://github.com/pythonguis/python-qtwidgets/tree/master/qtwidgets/toggle
# https://stackoverflow.com/questions/62363953/how-to-create-toggle-switch-button-in-qt-designer
class ColorSwitch(QCheckBox):
    _transparent_pen = QPen(Qt.GlobalColor.transparent)
    _light_grey_pen = QPen(Qt.GlobalColor.lightGray)
    _black_pen = QPen(Qt.GlobalColor.black)

    def __init__(self,
                parent = None,
                bar_color = Qt.GlobalColor.gray,
                checked_color = "#00B0FF",
                handle_color=Qt.GlobalColor.white, 
                h_scale=1.0,
                v_scale=1.0,
                fontSize=10):
        super().__init__(parent)
        self._bar_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())   
        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))

        self.setContentsMargins(8, 0, 8, 0)
        self._handle_position = 0
        self._h_scale = h_scale
        self._v_scale = v_scale
        self._font_size = fontSize

        self.stateChanged.connect(self.handle_state_change)

    def sizeHint(self):
        return QSize(58, 45)
        
    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)
        
    def paintEvent(self, e: QPaintEvent):
        contRect = self.contentsRect()
        width =  contRect.width() * self._h_scale
        height = contRect.height() * self._v_scale
        handleRadius = round(0.24 * height)

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.setPen(self._transparent_pen)
        barRect = QRectF(0, 0, width - handleRadius, 0.40 * height)
        barRect.moveCenter(QPointF(contRect.center()))
        rounding = barRect.height() / 2

        # the handle will move along this line
        trailLength = contRect.width()*self._h_scale - 2 * handleRadius
        xLeft = contRect.center().x() - (trailLength + handleRadius)/2 
        xPos = xLeft + handleRadius + trailLength * self._handle_position

        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)

            p.setPen(self._black_pen)
            p.setFont(QFont('Helvetica', self._font_size, 75))
            p.drawText(
                int(xLeft + handleRadius / 2),
                int(contRect.center().y() + handleRadius / 2),
                "COL",
            )

        else:
            p.setBrush(self._bar_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setPen(self._light_grey_pen)
            p.setBrush(self._handle_brush)

        p.setPen(self._light_grey_pen)
        p.drawEllipse(
            QPointF(xPos, barRect.center().y()),
            handleRadius, handleRadius)

        p.end()

    @Slot(int)
    def handle_state_change(self, value):
        self._handle_position = 1 if value else 0
        
    @Property(float)
    def handle_position(self):
        return self._handle_position
        
    @handle_position.setter
    def handle_position(self, pos):
        """change the property
        we need to trigger QWidget.update() method, either by:
        1- calling it here [ what we're doing ].
        2- connecting the QPropertyAnimation.valueChanged() signal to it.
        """
        self._handle_position = pos
        self.update()

    def setH_scale(self,value):
        self._h_scale = value
        self.update()

    def setV_scale(self,value):
        self._v_scale = value
        self.update()

    def setFontSize(self,value):
        self._fontSize = value
        self.update()
