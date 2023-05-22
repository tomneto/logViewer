import json
import os, sys
import os.path

from PyQt5.QtCore import QSize, QThread
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QMainWindow, QShortcut, QAction
from PyQt5.QtWidgets import QStatusBar, QApplication
from PyQt5.QtWidgets import QTabWidget, QWidget, QTabBar

from System import socketOS
from System import relativePath

from Themes import applyTheme, loadFonts

from GUI import Popups, Dialogs, custom
from GUI.Dialogs import openFileDialog
from GUI.DockedWidgets import findWidget, themeWidget
from GUI.Widgets import textEditor

import Settings

from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

class mainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.SettingsHandler = socketOS('Log Viewer')



content = {'patterns': [{'backgroundColorHex': '#ff000000', 'caseSensitive': False, 'pattern': 'lorem', 'style': 'color:#ff0433ff; background-color:#ff000000', 'textColorHex': '#ff0433ff'}, {'backgroundColorHex': '#ff942192', 'caseSensitive': False, 'pattern': 'a', 'style': 'color:#ffff2600; background-color:#ff942192', 'textColorHex': '#ffff2600'}], 'private': True, 'title': 'Banana'}

def standalone():
    app.processEvents()
    window = mainWindow()
    window.layout().addWidget(custom.SlideElement())

    #Dialogs.saveFileDialog(mainWindow=window, title='Choose Template Destination', fileExt='Template File (*.json)', content=json.dumps(content, indent=2))
    window.show()
    sys.exit(app.exec())

standalone()
