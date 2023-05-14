import os.path
import re
from datetime import datetime

from PyQt5.QtCore import QThreadPool, pyqtSlot, QObject, pyqtSignal
from PyQt5.QtGui import QTextDocument, QTextCursor, QCursor
from PyQt5 import Qt
from PyQt5.QtWidgets import QTabWidget, QWidget, QTabBar
from . import textEditor

class newTabDefinitions:
    def __init__(self, title):
        self.title = title



class mainTab(QTabWidget):
    def __init__(self, *args, mainWindow):
        super().__init__()
        self.thread_pool = QThreadPool.globalInstance()

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
                
                #for each in currentTabs:
                #    if each['id'] != currentPage:
                #        if each['id'] != 0:
                #            currentTabs[each['id']]['thread'].stop()

                print(f"Changing to tab {currentPage}")

                self.changeFocus(currentTabs, currentPage)

        except:
            raise Exception(f'Failed onChange to {currentPage}')

    def changeFocus(self, currentTabs, currentPage):
        self.mainWindow.SettingsHandler.setValue('selectedTableId', currentPage)

        currentTabs[currentPage]['textEditor'].thread.start()

        for page in currentTabs:
            if page['id'] > 0 and page['id'] != currentPage:
                page['textEditor'].thread.wait()

        self.mainWindow.findWidget.changeFocus(currentTabs[currentPage]['textEditor'])

        self.mainWindow.SettingsHandler.setObject('tabs', currentTabs)


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
                print(f'Creating text editor')
                newPage['textEditor'] = textEditor.QCodeEditor(mainWindow=self.mainWindow, index=currentId, file=file, pageData=newPage)

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
        else:
            return True

    def remove(self, tabIndex: int):
        currentTabs = self.mainWindow.SettingsHandler.getObject('tabs', [])
        currentOpenFiles = self.mainWindow.SettingsHandler.getSessionValue('openFiles', [])
        
        currentTabs[tabIndex]['textEditor'].thread.quit()
        currentTabs.remove(currentTabs[tabIndex])
        currentOpenFiles.remove(currentOpenFiles[tabIndex-1])
        self.removeTab(tabIndex)

        self.mainWindow.SettingsHandler.setObject('tabs', currentTabs)
        self.mainWindow.SettingsHandler.setSessionValue('openFiles', currentOpenFiles)
