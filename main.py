import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from Ui_login import Ui_MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QApplication([])

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())