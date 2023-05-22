import os
import re

from PyQt5.QtCore import QUrl, QDir
from PyQt5.QtWidgets import QFileDialog

from GUI import Popups
from config import inputSpecs

class openFileDialog(QFileDialog):
    def __init__(self, *args, mainWindow, fileExt, title='Choose your Destiny'):
        super().__init__()
        self.validFiles = False
        self.mainWindow = mainWindow

        if mainWindow:

            # Enable the built-in dock widget
            self.setSidebarUrls([QUrl.fromLocalFile(QDir.homePath())])

            self.setOptions(QFileDialog.DontUseNativeDialog)

            # Add recent files to the dialog
            recentFiles = self.mainWindow.SettingsHandler.getValue('recentFiles', [])
            self.setHistory(recentFiles)
            self.setAcceptMode(QFileDialog.AcceptOpen)

            # Get the selected file path
            self.filesToCheck, _ = self.getOpenFileName(self.mainWindow, title, f"{self.mainWindow.SettingsHandler.getValue('latestOpenFileDir', '')}",
                                                     fileExt, options=self.options())

    def checkFile(self, path):
        self.validFile = list()

        if self.checkExtension(path):
            if not any(openFile == path for openFile in self.mainWindow.SettingsHandler.getSessionValue('openFiles', [])):
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
            print(f'Opening {self.filesToCheck}')
            self.mainWindow.SettingsHandler.setValue('latestOpenFileDir', os.path.dirname(self.validFile[0]))

            if self.validFile[0]:
                return self.validFile[0]
            else:
                return False


class saveFileDialog(QFileDialog):
    def __init__(self, *args, mainWindow, content, fileExt:str, latestDirectory:str='', title='Choose your Destiny'):
        super().__init__()
        self.validFiles = False
        self.mainWindow = mainWindow
        self.fileExt = fileExt
        self.content = content

        if mainWindow:

            # Enable the built-in dock widget
            self.setOptions(QFileDialog.DontUseNativeDialog)

            # Get the selected file path
            self.filesToCheck, _ = self.getSaveFileName(None, caption=title, directory=latestDirectory,
                                                     filter=f"{fileExt}", options=self.options())

            requiredExt = re.sub(r'.*\((.*?)\)', r'\1', self.fileExt)

            FileExt = os.path.splitext(self.filesToCheck)[-1].lower()

            if requiredExt.replace('*', '') not in os.path.basename(self.filesToCheck): self.filesToCheck += requiredExt.replace('*', '')

            self.overwrite = True

            if self.overwrite:
                self.saveFileContent()

            else:
                self.popup = Popups.default(mainWindow=self.mainWindow)
                self.popup.error(title="Invalid File Extension",
                                                         message="Please choose a valid file extension.")

    def saveFileContent(self):
        try:
            os.makedirs(os.path.dirname(self.filesToCheck), exist_ok=True)
            with open(self.filesToCheck, 'w') as storageFile:
                storageFile.write(self.content)
                self.success = True
        except:
            self.success = False
