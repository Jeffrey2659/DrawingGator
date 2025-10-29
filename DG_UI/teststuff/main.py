import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListView, QFileDialog

from DG_UI import Ui_MainWindow


class MainApp(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("Drawing Gator")

        # Central widget
   
        self.actionUpload_Image.triggered.connect(self.upload_image)
        self.actionUpload_Gcode.triggered.connect(self.upload_gcode)

    def upload_image(self):
        print("Upload Image clicked")
        # returns a tuple (file path, selected filter)
        path, _ = QFileDialog.getOpenFileName(self, "Select image",
                                              filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if path:
            self.label.setText(f"Loaded image: {path}")
            self.plainTextEdit.setPlainText(f"Selected file:\n{path}")


    def upload_gcode(self):
        print("Upload Gcode clicked")
        path, _ = QFileDialog.getOpenFileName(self, "Select gcode file",
                                              filter="Gcode Files (*.gcode *.nc);;All Files (*)")
        if path:
            self.label.setText(f"Loaded gcode: {path}")
            self.plainTextEdit.setPlainText(f"Selected file:\n{path}")



  

  


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec())