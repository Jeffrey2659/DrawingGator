from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
       

        label = QLabel("Hello!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(label)

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)
#THis is how to add an icon to the toolbar
   # button_action = QAction(QIcon("bug.png"), "Your button", self)


   
    #. You must also pass in any QObject to act as the parent for the action — here we're passing self as a reference to our main window.
    # for QAction the parent element is passed in as the final argument.
        button_action = QAction("Your button", self)
        #self is a reference to the main window above
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.toolbar_button_clicked)
        toolbar.addAction(button_action)
        toolbar.addAction(button_action)
        button_action.setCheckable(True)


#the status tip is the text that appears in the status bar when you hover over the button
        self.setStatusBar(QStatusBar(self))
    def toolbar_button_clicked(self, s):
        print("click", s)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
