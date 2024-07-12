from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")

        self.button = QPushButton("Open Modal Dialog")
        self.button.clicked.connect(self.openModalDialog)

        layout = QVBoxLayout()
        layout.addWidget(self.button)

        # central_widget = QWidget()
        # central_widget.setLayout(layout)
        # self.setCentralWidget(central_widget)

    def openModalDialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Modal Dialog")
        dialog.setWindowModality(Qt.ApplicationModal)  # 设置为模态窗口

        label = QLabel("This is a modal dialog.")
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(label)

        dialog.setLayout(dialog_layout)
        dialog.exec()


app = QApplication([])
window = MainWindow()
window.show()
app.exec()