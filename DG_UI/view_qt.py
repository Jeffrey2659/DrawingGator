# view_qt.py
from typing import Optional
from PyQt6 import QtGui
from PyQt6 import QtCore
from PyQt6.QtWidgets import QFrame, QMainWindow, QFileDialog, QMessageBox, QProgressBar, QDockWidget, QSizePolicy, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtGui import QAction
from typing import Optional, List
from PyQt6.QtWidgets import QCheckBox, QMainWindow, QFileDialog, QMessageBox, QProgressBar, QDockWidget, QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtGui import QBrush, QColor, QFont, QPaintEvent, QPainter, QPen
from DG_UI import Ui_MainWindow
from PyQt6.QtCore import QPoint, QPointF, QRectF, QSize, Qt, pyqtSignal
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
    on_stop_clicked = None


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
            background-color: #f0f4f8;
        }
        
        /* Central Widget */
        QWidget {
            background-color: #f0f4f8;
            color: #4a4a4a;
        }
        
        QPushButton {
            background-color: #708090;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #a8d5ba;
            border: none;
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
            background-color: #dde3ea;
            color: #2c3e50;
        }

        QMenuBar::item:selected {
            background-color: #c5cdd6;
        }

        QMenu {
            background-color: #dde3ea;
            color: #2c3e50;
        }

        QMenu::item:selected {
            background-color: #c5cdd6;
        }
        
        QProgressBar {
            background-color: #ffffff;
            color: #536878;
            border: 1px solid #d3d3d3;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #c0c0c0;
            border-radius: 3px;
        }
        
        QDockWidget {
            color: #c0c0c0;
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

        # remove all the old widgets to reorganize them
        self.verticalLayout_2.removeWidget(self.connect)
        self.verticalLayout_2.removeWidget(self.sendGcode)
        self.verticalLayout_2.removeWidget(self.plainTextEdit)

        self.verticalLayout_2.takeAt(0)
        self.verticalLayout_2.takeAt(0)

#######################################################################
######## ADDING A WINDOW FOR THE CONNECTION ###########################

        self._conn_window = QWidget(self.centralwidget)
        # transparent background for the connection window
        self._conn_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        window_layout = QVBoxLayout(self._conn_window)
        # be centered
        window_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        conn_title = QFrame(self._conn_window)
        conn_title.setFixedSize(200, 140)
        conn_title.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #d9d9d9;
            }
        """)

        title_layout = QVBoxLayout(conn_title)
        title_layout.setContentsMargins(20, 20, 20, 20)
        title_layout.setSpacing(6)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        window_subtitle = QLabel("Connect to your Arduino to get started!")
        window_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window_subtitle.setWordWrap(True)
        window_subtitle.setStyleSheet(
            "font-size: 14px; color: #4a4a4a;"
            "background-color: transparent; border: none;"
        )

        window_button = QPushButton("Connect to Arduino")
        window_button.setFixedHeight(30)
        window_button.setCursor(Qt.CursorShape.PointingHandCursor)
        window_button.setStyleSheet("""
            QPushButton {
                background-color: #a8d5ba;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #a8d5d1;
                border: none;
            }
        """)
        window_button.clicked.connect(lambda: self.on_connect_clicked and self.on_connect_clicked())
        
##########################################################################
############ LEFT SIDE ######### RIGHT SIDE ##############################
############ Connect ########### SVG #####################################
############ Speed #######################################################
############ Toggle ######################################################

        # left size
        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)
        self.verticalLayout_2.addLayout(left_layout)   

        left_panel = QFrame(self.centralwidget)
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #fefefa;
                border-radius: 10px;
            }
        """)
        left_side = QVBoxLayout(left_panel)
        left_side.setContentsMargins(12, 12, 12, 12)
        left_side.setSpacing(6)

        # adding the svg here
        self.mpl_widget = MatplotlibWidget()
        self.mpl_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # right panel
        right_panel = QFrame(self.centralwidget)
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #d9d9d9;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # wrap container and buttons in one
        self.dashed_zone = QWidget()
        self.dashed_zone.setObjectName("dashedZone")
        self.dashed_zone.setFixedSize(250, 165)
        self.dashed_zone.setStyleSheet("""
            #dashedZone {
                border: 2px dashed #d2b48c;
                background-color: #ffffff;
                border-radius: 10px;
                color: #4a4a4a;
                font-size: 14px;
            }
            QPushButton {
                background-color: #708090;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a8d5ba;
                border: none;
            }
        """)

        dashed_zone_layout = QVBoxLayout(self.dashed_zone)
        dashed_zone_layout.setContentsMargins(16, 16, 16, 16)
        dashed_zone_layout.setSpacing(10)
        dashed_zone_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.drop_zone = DropZone()
        self.drop_zone.fileDropped.connect(lambda path: self.on_upload_svg and self.on_upload_svg(path))
        self.drop_zone.fileDropped.connect(lambda path: (self.dashed_zone.hide(), self.mpl_widget.show()))
        #right_layout.addWidget(self.drop_zone, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # add a separator
        or_separator = QLabel("————— or —————")
        or_separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        or_separator.setStyleSheet("color: #000000; font-size: 15px; border: none; background-color: transparent")

        # adding upload button here?
        self.image_upload = QPushButton("Upload Image")
        self.image_upload.setFixedHeight(28)
        self.image_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        self.image_upload.clicked.connect(self._ask_open_svg)

        dashed_zone_layout.addWidget(self.drop_zone)
        dashed_zone_layout.addWidget(or_separator)
        dashed_zone_layout.addWidget(self.image_upload, alignment=Qt.AlignmentFlag.AlignCenter)

        right_layout.addWidget(self.dashed_zone, alignment=Qt.AlignmentFlag.AlignCenter)        
        right_layout.addWidget(self.mpl_widget)

        self.mpl_widget.hide()

        left_layout.addWidget(left_panel)
        left_layout.addWidget(right_panel, stretch=1)

       

        #manual command dock
        # dock = QDockWidget("Manual Command", self)
        # dock.setObjectName("ManualCommandDock")
        # dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)


        # add the matplotlib widget for svg display
        # self.mpl_widget = MatplotlibWidget()
        # preview_dock = QDockWidget()
        # preview_dock.setObjectName("SVGPreviewDock")
        # preview_dock.setTitleBarWidget(QWidget())  # Hide the title bar
        # preview_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        # preview_dock.setWidget(self.mpl_widget)
        # preview_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
        #                           QDockWidget.DockWidgetFeature.DockWidgetFloatable 
        #                           )
        # self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, preview_dock)
        
        # Set initial size for the dock (optional but helpful)
        # preview_dock.setMinimumWidth(300)
        # w = QWidget(dock)
        # lay = QHBoxLayout(w)
        # lay.setContentsMargins(8, 8, 8, 8)

        # self.manualLine = QLineEdit(w)
        # self.manualLine.setPlaceholderText("Type a G-code, e.g. G0 X10 Y10 (Enter to send)")
        # self.manualSendBtn = QPushButton("Send", w)

        # lay.addWidget(self.manualLine, 1)
        # lay.addWidget(self.manualSendBtn, 0)

        # w.setLayout(lay)
        # dock.setWidget(w)
        # self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)


##############################################################################
################## CONNECTION STATUS #########################################
        # connection status 
        # dot is red to begin with
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(12, 12)
        self.status_dot.setStyleSheet("background-color: red; border-radius: 6px;")
        
        # put the label
        self.status_text = QLabel("Disconnected", )
        self.status_text.setStyleSheet("color: #4a4a4a; font-weight: bold;")
        
        status_section = QWidget()
        status_section.setStyleSheet("background: transparent;")
        status_layout = QHBoxLayout(status_section)
        status_layout.setContentsMargins(0, 2, 0, 2)
        status_layout.setSpacing(6)
        status_layout.addWidget(self.status_dot)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()

        # connect to functionality of connect
        self.connect.setStyleSheet(
            "background-color: #a8d5ba; color: #ffffff; border: none;"
            "border-radius: 4px; padding: 8px 16px; font-weight: bold;"
        )

        connection_label = QLabel("Connection Status:")
        connection_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        connection_label.setStyleSheet("color: #4a4a4a; font-weight: bold; font-size: 15px; border-bottom: 1px solid #d9c5a0; padding-bottom: 4px; border-radius: 0px;")
        left_side.addWidget(connection_label)
        left_side.addWidget(status_section)
        left_side.addWidget(self.connect, alignment=Qt.AlignmentFlag.AlignCenter)

        # Speed preset buttons
        # speed_container = QWidget(self.centralwidget)
        # speed_layout = QHBoxLayout(speed_container)
        # speed_layout.setContentsMargins(8, 4, 8, 4)
        # speed_layout.addWidget(QLabel("Draw Speed:"))

        self._btn_slow   = QPushButton("Slow\n(50 q-in/min)")
        self._btn_normal = QPushButton("Normal\n(100 q-in/min)")
        self._btn_fast   = QPushButton("Fast\n(200 q-in/min)")


        # for btn in (self._btn_slow, self._btn_normal, self._btn_fast):
        #     speed_layout.addWidget(btn)

        self._speed_buttons = {
            "slow":   self._btn_slow,
            "normal": self._btn_normal,
            "fast":   self._btn_fast,
        }

        # Insert before plainTextEdit in the central layout
        #idx = self.verticalLayout_2.indexOf(self.plainTextEdit)
        #self.verticalLayout_2.insertWidget(idx, speed_container)

        # Wire up clicks
        self._btn_slow.clicked.connect(lambda: self._on_speed_btn("slow"))
        self._btn_normal.clicked.connect(lambda: self._on_speed_btn("normal"))
        self._btn_fast.clicked.connect(lambda: self._on_speed_btn("fast"))

        # Highlight normal as the default
        self._highlight_speed_btn("normal")

        speed_label = QLabel("Speed Controls:")
        speed_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        speed_label.setStyleSheet("color: #4a4a4a; font-weight: bold; font-size: 15px; border-bottom: 1px solid #d9c5a0; padding-bottom: 4px; border-radius: 0px;")
        left_side.addWidget(speed_label)
        left_side.addWidget(self._btn_slow, alignment=Qt.AlignmentFlag.AlignCenter)
        left_side.addWidget(self._btn_normal, alignment=Qt.AlignmentFlag.AlignCenter)
        left_side.addWidget(self._btn_fast, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status progress bar (no .ui changes needed)
        self._progress = QProgressBar(self)
        self._progress.setMinimum(0)
        self._progress.setMaximum(0)
        self._progress.setValue(0)
        self._progress.setFormat("0/0")
        self._progress.setTextVisible(True)
        self.statusbar.addPermanentWidget(self._progress, 1)

        gcode_label = QLabel("Begin Job:")
        gcode_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        gcode_label.setStyleSheet("color: #4a4a4a; font-weight: bold; font-size: 15px; border-bottom: 1px solid #d9c5a0; padding-bottom: 4px; border-radius: 0px;")
        left_side.addWidget(gcode_label)
        left_side.addWidget(self.sendGcode, alignment=Qt.AlignmentFlag.AlignCenter)

        # toggle 
        self.toggle_switch = ColorSwitch(
            checked_color="#708090",
            h_scale = 1.5,
            v_scale = 1.5,
        )
        color_label = QLabel("Change to color/grayscale:")
        color_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        color_label.setStyleSheet("color: #4a4a4a; font-weight: bold; font-size: 15px; border-bottom: 1px solid #d9c5a0; padding-bottom: 4px; border-radius: 0px;")
        left_side.addWidget(color_label)
        left_side.addWidget(self.toggle_switch, alignment=Qt.AlignmentFlag.AlignCenter)
    
        # add the progress below the toggle
        status_label = QLabel("Progress Bar:")
        status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        status_label.setStyleSheet("color: #4a4a4a; font-weight: bold; font-size: 15px; border-bottom: 1px solid #d9c5a0; padding-bottom: 4px; border-radius: 0px;")
        self.ready_dot = QLabel()
        self.ready_dot.setFixedSize(12, 12)
        self.ready_dot.setStyleSheet("background-color: red; border-radius: 6px;")
        
        # put the label
        self.ready_text = QLabel("Not ready", )
        self.ready_text.setStyleSheet("color: #4a4a4a; font-weight: bold;")
        ready_section = QWidget()
        ready_section.setStyleSheet("background: transparent;")
        status_layout = QHBoxLayout(ready_section)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(6)
        status_layout.addWidget(self.ready_dot)
        status_layout.addWidget(self.ready_text)
        left_side.addWidget(status_label)
        left_side.addWidget(ready_section)
        left_side.addWidget(self._progress)

        #self.statusbar.addWidget(self.toggle_switch)
        self.toggle_switch.toggled.connect(self._on_color_clicked)

        # manual send

        self.on_manual_send = None
        # UI -> Presenter callbacks
        #if no lambda then it calls the function immediately instead of waiting for the button to be clicked
        #the lambda creates an anonymous function that calls the function when the button is clicked
        # Replace the bare sendGcode button with a Send + Stop row
        send_idx = self.verticalLayout_2.indexOf(self.sendGcode)
        self.verticalLayout_2.removeWidget(self.sendGcode)

        send_row = QWidget(self.centralwidget)
        send_row_layout = QHBoxLayout(send_row)
        send_row_layout.setContentsMargins(0, 0, 0, 0)
        send_row_layout.addWidget(self.sendGcode)

        self.stopBtn = QPushButton("Stop", send_row)
        self.stopBtn.setStyleSheet(
            "background-color: #e07070; color: #fff; border: 1px solid #c05050;"
            "border-radius: 4px; padding: 6px 12px; font-weight: bold;"
        )
        send_row_layout.addWidget(self.stopBtn)
        self.verticalLayout_2.insertWidget(send_idx, send_row)

        self.connect.clicked.connect(lambda: self.on_connect_clicked and self.on_connect_clicked())
        self.sendGcode.clicked.connect(lambda: self.on_send_clicked and self.on_send_clicked())
        self.stopBtn.clicked.connect(lambda: self.on_stop_clicked and self.on_stop_clicked())
        self.actionUpload_Gcode.triggered.connect(lambda: self.on_upload_clicked and self.on_upload_clicked())



        ####################################################### 
        ###### MAKING QUESTION MARK FOR FAQ OR HOW TO USE #####
        # self._help_button = QPushButton("?", self.centralwidget)
        # self._help_button.setFixedSize(30, 30)
        # self._help_button.setStyleSheet("""
        #     QPushButton {
        #         background-color: #708090;
        #         color: #ffffff;
        #         border: none;
        #         border-radius: 15px;
        #         font-weight: bold;
        #     }
            
        #     QPushButton:hover {
        #         background-color: #a8d5ba;
        #         border: none;
        #     }
        # """)
        # self._help_button.clicked.connect(self._show_faq)
                                        
        # manual present callbacks
        # self.manualLine.returnPressed.connect(self._send_manual_from_line)
        # self.manualSendBtn.clicked.connect(self._send_manual_from_button)


        #svg upload
        #this is mapped to the uploadImage button rn, I might add a separate button later
        self.actionUpload_Image.triggered.connect(self._ask_open_svg)

        # Draw Text menu action
        self.actionDraw_Text = QAction("Draw Text", self)
        self.menuMenu.addAction(self.actionDraw_Text)
        self.actionDraw_Text.triggered.connect(self._ask_draw_text)

        # adding a help functionality
        help_bar = self.menuBar().addMenu("Help")
        
        how_to_use = QAction("How to Use", self)
        how_to_use.triggered.connect(self._how_to_use)
        help_bar.addAction(how_to_use)

        faq_section = QAction("FAQ", self)
        faq_section.triggered.connect(self._show_faq)
        help_bar.addAction(faq_section)
        # If you add Pause/Resume buttons in .ui (names: pauseBtn/resumeBtn), hook them:
        # self.pauseBtn.clicked.connect(lambda: self.on_pause_clicked and self.on_pause_clicked())
        # self.resumeBtn.clicked.connect(lambda: self.on_resume_clicked and self.on_resume_clicked())
        #self.actionUpload_Image.triggered.connect(self._ask_open_image)    # Presenter -> View API
        self.colorButton.hide()
        # remove the text window
        self.plainTextEdit.hide()
        # hide the manulal command also
        #self.manualLine.hide()
        #self.manualSendBtn.hide()
        #self.create_show_svg_preview()

        title_layout.addWidget(window_subtitle)
        title_layout.addWidget(window_button)
        window_layout.addWidget(conn_title)

        # hide the connect 
        self.connect.hide()

        self._conn_window.resize(self.centralwidget.size())
        self._conn_window.raise_()
        self._conn_window.show()
        #self._help_button.raise_()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_conn_window"):
            self._conn_window.resize(self.centralwidget.size())
        # if hasattr(self, "_help_button"):
        #     self._help_button.move(
        #         self.centralwidget.width() - 35,
        #         self.centralwidget.height() - 20
        #     )
# REFERENCE: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QMessageBox.html
    def _show_faq(self):
        faq_text = ("FAQ - How to proceed if stuck\n\n"
                    "1. Why isn't an image being processed?'.\n"
                    "  --- Check that the format is correct.\n"
                    "2. Why change the speed?.\n"
                    "  --- \n"
                    "3. What happens if I don't like the drawing?\n"
                    "  --- You can stop and retry (small glitches may happen don't worry).\n"

                    )
        QMessageBox.information(self, "FAQ - How to Use", faq_text)

    def _how_to_use(self):
        how_to_text = (
            "How to use the app:\n\n"
            "- IMPORTANT: Need to connect to the device\n"
            "- You can upload any image in any format (e.g jpeg, jpg, png, svg, bmp)\n"
            "- After loading in Progess Bar, 'Ready' with a green light with display to show that everything is ready to proceed\n"
            "- A toggle switch is located in the left panel, if you wish to switch from grayscale to color\n"
            "- If you are satisfied with the output proceed to 'Start Drawing' button\n"
            "- Follow the progress in the Progess Bar section\n"
            "\nNote: Images are set to be grayscale by default."
        )
        QMessageBox.information(self, "How to", how_to_text)

    def _on_color_clicked(self, checked: bool):
            if checked:
                if self.on_color_clicked:
                    self.on_color_clicked()
            else:
                if self.on_grayscale_clicked:
                    self.on_grayscale_clicked()

    def set_connected(self, connected: bool, desc: str = "") -> None:
        if connected:
            self.status_dot.setStyleSheet("background-color: green; border-radius: 6px;")
            self.status_text.setText("Connected")
            self.connect.setText("Disconnect")
            self.connect.setStyleSheet(
                "background-color: #f08080; color: #ffffff; border: none;"
                "border-radius: 4px; padding: 8px 16px; font-weight: bold;"
            )
            # remove connetion window
            self.connect.show()
            self._conn_window.hide()
        else:
            self.status_dot.setStyleSheet("background-color: red; border-radius: 6px;")
            self.status_text.setText("Disconnected")
            self.connect.setText("Connect to Arduino")
            self.connect.setStyleSheet(
                "background-color: #a8d5ba; color: #ffffff; border: none;"
                "border-radius: 4px; padding: 8px 16px; font-weight: bold;"
            )   
            self.connect.hide()
            self._conn_window.resize(self.centralwidget.size())
            self._conn_window.raise_()
            self._conn_window.show()
        
        #self.connect.setText("Disconnect" if connected else "Connect to Arduino")
        self.statusbar.showMessage(desc if connected else "Disconnected", 3000)

    def set_progress(self, sent: int, total: int) -> None:
        total = max(1, total)
        self._progress.setMaximum(total)
        self._progress.setValue(sent)
        self._progress.setFormat(f"{sent}/{total}")
        is_loaded_job = total > 1
        if is_loaded_job and sent < total:
            self.ready_dot.setStyleSheet("background-color: green; border-radius: 6px;")
            self.ready_text.setText("Ready:")
        else:
            self.ready_dot.setStyleSheet("background-color: red; border-radius: 6px;")
            self.ready_text.setText("Not ready")

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
            self.dashed_zone.hide()
            self.mpl_widget.show()


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
        return QSize(40, 20)
        
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

# Making class for a drag and drop zone
# REFERENCE: https://woteq.com/how-to-implement-drag-and-drop-file-upload-in-pyqt-using-python
# https://www.tutorialspoint.com/pyqt/pyqt_drag_and_drop.htm
# https://en.ittrip.xyz/python/pyqt-drag-drop-guide 
class DropZone(QLabel):
    fileDropped = pyqtSignal(str)
    ask_open_svg = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Drop Image Here ...")
        self.setAcceptDrops(True)

        # fixed size
        self.setFixedSize(200, 100)

        self.setStyleSheet("""
            QLabel {
                border: none;
                background-color: transparent;
                font-size: 14px;
            }
        """)


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = str(url.toLocalFile())
                self.processFile(file_path)
            event.accept()

    def processFile(self, file_path):
        image = QtGui.QImage(file_path)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.setPixmap(pixmap.scaled(self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        self.fileDropped.emit(file_path)