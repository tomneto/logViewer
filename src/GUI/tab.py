import os.path
import re
from datetime import datetime

from PyQt5.QtGui import QTextDocument, QTextCursor
from PyQt5.QtWidgets import QTabWidget, QWidget, QTabBar
from . import textEditor
from .. import Threads

class newTabDefinitions:
    def __init__(self, title):
        self.title = title

class mainTab(QTabWidget):
    def __init__(self, *args, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.setMovable(False)
        self.setTabsClosable(True)
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.doc = QTextDocument()
        self.blankPage()

        self.tabBarClicked.connect(self.newTabButton)
        self.currentChanged.connect(self.onChange)
        self.setUpdatesEnabled(True)
        self.tabCloseRequested.connect(self.onCloseEvent)

    def newTabButton(self, tab):
        if tab == 0:
            self.showOpenFileDialog()

    def showTab(self, id):
        currentTabs = self.mainWindow.SettingsHandler.getObject('tabs', [])
        
        filename = os.path.basename(currentTabs[id]['file'])
        self.addTab(currentTabs[id]['textEditor'], f'{filename}')
        self.setCurrentIndex(id)

        self.mainWindow.SettingsHandler.setObject('tabs', currentTabs)

    def onChange(self, currentPage):
        try:
            if currentPage != 0:
                currentTabs = self.mainWindow.SettingsHandler.getObject('tabs', [])
                
                for each in currentTabs:
                    if each['id'] != currentPage:
                        if each['id'] != 0:
                            currentTabs[each['id']]['thread'].stop()

                self.mainWindow.SettingsHandler.setValue('selectedTableId', currentPage)
                currentTabs[currentPage]['thread'].watch(currentTabs[currentPage])

                self.mainWindow.findWidget.changeFocus(currentTabs[currentPage]['textEditor'])

                self.mainWindow.SettingsHandler.setObject('tabs', currentTabs)
        except:
            raise Exception(f'Failed onChange to {currentPage}')

    def blankPage(self):
        blankWidget = QWidget()
        blankWidget.setObjectName('blankTab')

        self.mainWindow.SettingsHandler.setObject('logViewerHome', blankWidget)

        self.openFile('', blankWidget)

        self.addTab(blankWidget, '+')
        self.tabBar().setTabButton(0, QTabBar.LeftSide, None)

    def show(self):
        self.mainWindow.setCentralWidget(self.mainWindow.tab)

    def openFile(self, file: str, widget=None):
        try:
            currentTabs = self.mainWindow.SettingsHandler.getObject('tabs', [])
        
            currentId = len(currentTabs)
            newPage = dict()
            newPage['id'] = currentId
            newPage['file'] = file
            newPage['parent'] = self
            newPage['codeEditorCount'] = 0

            if widget is not None:
                newPage['textEditor'] = widget
            else:
                newPage['textEditor'] = textEditor.QCodeEditor(mainWindow=self.mainWindow)
            newPage['thread'] = Threads.logReader(parent=self, index=currentId, file=file)

            currentTabs.append(newPage)
            self.mainWindow.SettingsHandler.setObject('tabs', currentTabs)

            self.showTab(currentId)

        except:
            pass

    def showOpenFileDialog(self):
        self.mainWindow.chooseLogFile()

    def onCloseEvent(self, tabIndex: int):
        if tabIndex != 0:
            self.mainWindow.statusBar.showMessage('')
            self.remove(tabIndex)

    def remove(self, tabIndex: int):
        currentTabs = self.mainWindow.SettingsHandler.getObject('tabs', [])
        currentOpenFiles = self.mainWindow.SettingsHandler.getSessionValue('openFiles', [])
        
        currentTabs[tabIndex]['thread'].stop()
        currentTabs.remove(currentTabs[tabIndex])
        currentOpenFiles.remove(currentOpenFiles[tabIndex-1])
        self.removeTab(tabIndex)

        self.mainWindow.SettingsHandler.setObject('tabs', currentTabs)
        self.mainWindow.SettingsHandler.setSessionValue('openFiles', currentOpenFiles)
