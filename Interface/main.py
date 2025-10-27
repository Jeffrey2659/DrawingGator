import sys
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication, QPushButton, QMainWindow





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        self.buttonCheck = True
        self.setWindowTitle("My App")
    

        self.setFixedSize(QSize(300, 200))
        #can also set minimum and maximum size
        #self.setMinimumSize(QSize(300, 200))   
        #self.setMaximumSize(QSize(300, 200))

        self.button = QPushButton("Press Me")
        self.button.clicked.connect(self.buttonClicked)

       # button.clicked.connect(self.buttonClicked)
        self.setCentralWidget(self.button)



    def buttonClicked(self):
        self.button.setText("You Pressed Me")
        self.button.setEnabled(False)

        self.setWindowTitle("My App - Pressed")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()