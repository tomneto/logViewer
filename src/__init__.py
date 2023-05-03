import os
import sys
from PyQt5.QtWidgets import QApplication

from src.GUI import mainWindow

# DEV VARIABLES
app = QApplication(sys.argv)

def trayStart():
    logViewer = mainWindow()
    logViewer.chooseLogFile()

def standalone():
    app.processEvents()
    window = mainWindow()
    window.show()
    app.exec()

