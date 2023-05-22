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

    def askYesOrNo(self, message, title):
        self.setIcon(self.Question)
        self.setText(message)
        self.setWindowTitle(title)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        self.clicked = self.exec_()

        if self.clicked == QMessageBox.Yes:
            return True
        else:
            return False