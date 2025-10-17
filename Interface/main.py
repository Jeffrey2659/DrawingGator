import sys
<<<<<<< Updated upstream
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
=======
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout, QFileDialog, QLabel, QMessageBox
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
>>>>>>> Stashed changes

# load the algorithm
from svg_algorithm import conversion_svg, animation_simulation
'''
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
'''

class LoadImage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Load Image Example")
        self.setGeometry(100, 100, 300, 200)

        # load an image button
        self.upload_button = QPushButton("Load Image")
        self.upload_button.clicked.connect(self.load_image)
        layout = QVBoxLayout()
        layout.addWidget(self.upload_button)

        # area to display the svg
        self.svg_area = QSvgWidget()
        self.svg_area.setFixedSize(400, 400)
        layout.addWidget(self.svg_area)
        self.setLayout(layout)


    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg)")
        if not file_path:
            return
        try:
            conversion_svg(file_path, output_path="output.svg")
            self.svg_area.load("output.svg")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoadImage()
    window.show()
    sys.exit(app.exec())