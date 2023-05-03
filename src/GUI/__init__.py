import os.path
import sys

from src.Common.system import relativePath
from src.Common.themes import applyTheme, loadFonts

from PyQt5.QtWidgets import QStatusBar

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMainWindow, QShortcut, QAction

from .. import Settings
from src.Common.gui.titleBar import CustomTitleBar
from src.Common.settings import socketIO
from src.Common.gui.Dialogs import openLogFileDialog

from .DockedWidgets import findWidget, themeWidget

from .tab import mainTab

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the main window
        self.initialValues()

        applyTheme(self, relativePath(os.path.join('Themes')), 'darkTheme')
        loadFonts(relativePath(os.path.join('Fonts')))

        self.SettingsHandler = socketIO('Log Viewer')
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Set window properties
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.SettingsHandler.setValue('findTitle', 'Log Viewer - Finder')
        self.SettingsHandler.setValue('headerLabels', ['Log Content'])
        self.setWindowTitle(self.SettingsHandler.getValue('title'))
        self.setWindowSize()
        self.shortcuts()
        self.mainMenu()
        self.titleBar = CustomTitleBar(self.menuBar, self)
        self.setMenuWidget(self.titleBar)

        # Load Dock Widgets
        self.loadDockWidgets()

        # Load Components
        self.loadComponents()

    def initialValues(self):
        self.logPath = None
        self.cleanRecentFiles = None
        self._pressed = False

    def setWindowSize(self):
        self.setMinimumSize(800, 800)
        defaultSizeX, defaultSizeY = self.SettingsHandler.getValue('sizeX', 800), self.SettingsHandler.getValue('sizeY', 800)
        self.resize(QSize(defaultSizeX, defaultSizeY))

    def loadDockWidgets(self):

        self.findWidget = findWidget()
        self.addDockWidget(Qt.TopDockWidgetArea, self.findWidget)
        self.findWidget.hide()

        self.themeWidget = themeWidget(self.SettingsHandler)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.themeWidget)
        self.themeWidget.hide()

    def loadComponents(self):
        self.tabIndex = self.SettingsHandler.getValue('tabIndex', 0)
        self.tab = mainTab(mainWindow=self)
        self.setCentralWidget(self.tab)

    def resizeEvent(self, event):
        self.SettingsHandler.setValue('sizeX', self.size().width())
        self.SettingsHandler.setValue('sizeY', self.size().height())

    def mainMenu(self):
        menubar = self.menuBar()

        # MENU
        fileMenu = menubar.addMenu('File')

        # FILE MENU
        openLog = QAction(f'Open Log [{Settings.logViewerSettings.shortcuts["openFileDialog"]}]', self)
        openLog.triggered.connect(self.chooseLogFile)
        fileMenu.addAction(openLog)

        # RECENT FILES

        self.recentFileMenu = fileMenu.addMenu('Open Recent')

        if self.SettingsHandler.getValue('recentFiles'):
            uniqueRencentFiles = set(self.SettingsHandler.getValue('recentFiles'))
            for each in uniqueRencentFiles:
                if os.path.isfile(each):
                    self.appendMenuRecentFile(each)
                else:
                    pass

        # EDIT
        edit = menubar.addMenu('Edit')

        find = QAction(f'Find [{Settings.logViewerSettings.shortcuts["find"]}]', self)
        find.triggered.connect(self.showFindWidget)

        edit.addAction(find)

        # VIEW
        viewMenu = menubar.addMenu('View')

        wordWrap = QAction(f'Word Wrap [{Settings.logViewerSettings.shortcuts["wordWrap"]}]', self)
        wordWrap.triggered.connect(self.changeWordWrap)

        viewMenu.addAction(wordWrap)

        return menubar

    def shortcuts(self):
        QShortcut(QKeySequence(Settings.logViewerSettings.shortcuts['openFileDialog']), self).activated.connect(self.chooseLogFile)
        QShortcut(QKeySequence(Settings.logViewerSettings.shortcuts['closeTab']), self).activated.connect(self.closeTab)
        QShortcut(QKeySequence(Settings.logViewerSettings.shortcuts['find']), self).activated.connect(self.showFindWidget)
        QShortcut(QKeySequence(Settings.logViewerSettings.shortcuts['wordWrap']), self).activated.connect(self.changeWordWrap)
        QShortcut(QKeySequence(Settings.logViewerSettings.shortcuts['themeSelector']), self).activated.connect(self.showThemeWidget)

    def closeTab(self):
        self.tab.onCloseEvent(self.tab.currentIndex())

    def chooseLogFile(self):
        try:
            if not self.isVisible():
                self.setVisible(False)

            self.openFileDialog = openLogFileDialog(mainWindow=self)
            self.selectedFile = self.openFileDialog.getSelectedFiles()

            if self.selectedFile is not None:
                if not self.isVisible():
                    self.show()

                self.statusBar#.showMessage(f'Loading {self.selectedFile}')
                self.SettingsHandler.setValue('processingModelsItems', True)
                self.openLogFile(self.selectedFile)
                self.SettingsHandler.setValue('processingModelsItems', False)

            else:
                if not self.isVisible():
                    self.close()

        except:
            return False

    def openLogFile(self, filepath: str):
        if filepath not in self.SettingsHandler.getSessionValue('openFiles', []):
            self.appendOpenFile(filepath)
            self.tab.openFile(filepath)

    def closeEvent(self, event):
        self.SettingsHandler.saveConfig()
        self.destroy(True, True)
        sys.exit(0)

    def appendOpenFile(self, file: str):
        currentOpenedFiles = self.SettingsHandler.getSessionValue('openFiles', [])
        currentOpenedFiles.append(file)
        self.SettingsHandler.setSessionValue('openFiles', currentOpenedFiles)
        self.appendMenuRecentFile(file)

    def appendMenuRecentFile(self, file: str):
        try:
            currentVar = self.__getattribute__(file)
        except:
            currentVar = ''

        currentRecentFiles = self.SettingsHandler.getValue('recentFiles', [])

        if currentVar not in self.recentFileMenu.actions():
            currentRecentFiles.append(str(file))
            self.__setattr__(file, QAction(file, self))
            self.__getattribute__(file).triggered.connect(lambda: self.openLogFile(file))

            try:
                self.recentFileMenu.insertAction(self.recentFileMenu.menuAction(), self.__getattribute__(file))
            except:
                self.recentFileMenu.addAction(self.__getattribute__(file))

        else:
            currentRecentFiles.remove(str(file))
            self.recentFileMenu.removeAction(currentVar)

            currentRecentFiles.append(str(file))
            self.__setattr__(file, QAction(file, self))
            self.__getattribute__(file).triggered.connect(lambda: self.openLogFile(file))

            try:
                self.recentFileMenu.insertAction(self.recentFileMenu.actions()[0], self.__getattribute__(file))
            except:
                self.recentFileMenu.addAction(self.__getattribute__(file))

        self.SettingsHandler.setValue('recentFiles', currentRecentFiles)

    def showFindWidget(self):
        if self.findWidget.isVisible():
            self.findWidget.hide()
        else:
            self.findWidget.show()

    def showThemeWidget(self):
        if self.themeWidget.isVisible():
            self.themeWidget.hide()
        else:
            self.themeWidget.show()

    def changeWordWrap(self):
        currentTabs = self.SettingsHandler.getObject('tabs', [])

        for tab in currentTabs:
            if tab['id'] != 0:
                tab['textEditor'].changeWordWrap()
        self.SettingsHandler.setValue('wordWrapState', not self.SettingsHandler.getValue('wordWrapState', True))

        self.SettingsHandler.setObject('tabs', currentTabs)

    def changeColorTemplate(self):
        currentTabs = self.SettingsHandler.getObject('tabs', [])

        for tab in currentTabs:
            if tab['id'] != 0:
                tab['textEditor'].changeColorTemplate()

        self.SettingsHandler.setObject('tabs', currentTabs)
