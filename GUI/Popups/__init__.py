import sys

from PyQt5.QtWidgets import QMessageBox

class default(QMessageBox):

    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow

    def error(self, message, title):
        self.setIcon(self.Information)
        self.setText(message)
        self.setWindowTitle(title)
        self.setStandardButtons(QMessageBox.Ok)
        return self.show

