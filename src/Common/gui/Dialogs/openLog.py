import os
import re

from PyQt5.QtCore import QUrl, QDir
from PyQt5.QtWidgets import QFileDialog

from src.Common.gui import Popups
from src.config import inputSpecs


class openLogFileDialog(QFileDialog):
    def __init__(self, *args, mainWindow, title='Choose your Destiny'):
        super().__init__()
        self.validFiles = False
        self.mainWindow = mainWindow

        self.popup = Popups.default(mainWindow=self.mainWindow)
        self.errorPopup = self.popup.error(title="Invalid File Extension", message="Please choose a valid file.")
        if mainWindow:

            # Enable the built-in dock widget
            self.setSidebarUrls([QUrl.fromLocalFile(QDir.homePath())])

            self.setOptions(QFileDialog.DontUseNativeDialog)

            # Add recent files to the dialog
            recentFiles = self.mainWindow.SettingsHandler.getValue('recentFiles', [])
            self.setHistory(recentFiles)
            self.setAcceptMode(QFileDialog.AcceptOpen)
            # Get the selected file path
            self.filesToCheck, _ = self.getOpenFileName(self.mainWindow, title, f"{self.mainWindow.SettingsHandler.getValue('lastSelectedFolder', '')}",
                                                     "All Files (*);;Log Files (*.log)", options=self.options())

    def checkFile(self, path):
        self.validFile = list()

        if self.checkExtension(path):
            if not any(openFile == path for openFile in self.mainWindow.SettingsHandler.getSessionValue('openFiles', [])):
                print(f'Opening {path}')
                self.validFile.append(path)
                return self.validFile
            else:
                return False

    def checkExtension(self, path):
        if not input:
            return None
        else:
            FileExt = os.path.splitext(path)[-1].lower()
        if re.match(f"{inputSpecs['extension']}", FileExt) or re.match(f"{inputSpecs['extension']}[^0-9]", FileExt):
            return True
        else:
            return False

    def getSelectedFiles(self):
        if not self.filesToCheck:
            return None
        if self.checkFile(self.filesToCheck):
            self.mainWindow.SettingsHandler.setValue('lastSelectedFolder', os.path.dirname(self.validFile[0]))
            return self.validFile[0]
        else:
            self.errorPopup()
