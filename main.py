import sys
from PyQt6.QtWidgets import QApplication, QWidget
# from mainpage import Ui_Form
from PyQt6 import uic


class window(QWidget):
    def __init__(self):
        super().__init__()

        # use the Ui_login_form.py
        # self.ui = Ui_Form()
        self.ui = uic.loadUi(r'D:\pyve\HexoAutoDeploy\UI\mainpage.ui', self)
        # self.ui.setupUi(self)

        # show the login window
        self.show()
        # authenticate when the login button is clicked
        self.ui.uploadButton.clicked.connect(self.upload)
        self.ui.deployButton.clicked.connect(self.deploy)
        self.ui.backupButton.clicked.connect(self.backup)

    def upload(self):
        print('upload')

    def deploy(self):
        print('deploy')

    def backup(self):
        print('backup')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = window()
    sys.exit(app.exec())