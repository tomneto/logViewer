import os
import sys
from PyQt5.QtWidgets import QApplication

from GUI import mainWindow

# DEV VARIABLES
app = QApplication(sys.argv)

def trayStart():
    logViewer = mainWindow()
    logViewer.chooseLogFile()

def standalone():
    app.processEvents()
    window = mainWindow()
    window.show()
    sys.exit(app.exec())

#standalone()