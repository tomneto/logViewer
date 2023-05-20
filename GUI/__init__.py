import os
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

from GUI import Popups
from GUI.Dialogs import openLogFileDialog
from GUI.DockedWidgets import findWidget, themeWidget
from GUI.Widgets import textEditor

import Settings

class tabs(QTabWidget):

	def __init__(self, *args, mainWindow):
		super().__init__()
		self.thread_pool = QThreadPool.globalInstance()

		self.mainWindow = mainWindow
		self.setMovable(False)
		self.setTabsClosable(True)
		self.setTabPosition(QTabWidget.TabPosition.North)
		self.blankPage()

		self.tabBarClicked.connect(self.newTabButton)
		self.currentChanged.connect(self.onChange)
		self.setUpdatesEnabled(True)
		self.tabCloseRequested.connect(self.onCloseEvent)

		self.thread = QThread()
		self.thread.start()

		self.standby = QThread()
	def newTabButton(self, tab):
		if tab == 0:
			self.showOpenFileDialog()

	def showTab(self, index):
		#appendTabThread(self, index).start()
		currentTabs = self.mainWindow.SettingsHandler.getObject('tabs', [])
		filename = os.path.basename(currentTabs[index]['file'])
		self.addTab(currentTabs[index]['textEditor'], f'{filename}')
		self.setCurrentIndex(index)
		self.mainWindow.SettingsHandler.setObject('tabs', currentTabs)

	def onChange(self, currentPage):
		try:
			currentTabs = self.mainWindow.SettingsHandler.getObject('tabs', [])

			if currentPage != 0:
				self.changeFocus(currentTabs, currentPage)

		except:
			raise Exception(f'Failed onChange to {currentPage}')

	def changeFocus(self, currentTabs, currentPage):
		print('Change focus')
		self.mainWindow.SettingsHandler.setValue('selectedTableId', currentPage)

		for eachPage in currentTabs:
			if eachPage['id'] > 0 and eachPage['id'] != currentPage:
				print('Waiting')
				eachPage['textEditor'].fileReader.moveToThread(self.standby)
				#eachPage['textEditor'].thread.wait()

		if self.thread.isRunning() and not currentTabs[currentPage]['textEditor'].fileReader.isRunning():
			currentTabs[currentPage]['textEditor'].fileReader.start()
		elif self.thread.isRunning() and currentTabs[currentPage]['textEditor'].fileReader.isRunning():
			currentTabs[currentPage]['textEditor'].fileReader.moveToThread(self.thread)
			print('fileReader Started')
			#currentTabs[currentPage]['textEditor'].parent.thread.start()

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
				# newPage['threadPool'] = threadPool
				newPage['textEditor'] = textEditor.QCodeEditor(mainWindow=self.mainWindow, index=currentId, file=file, pageData=newPage, parent=self)

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
		print(f'Removing tab %d...' % tabIndex)
		currentTabs = self.mainWindow.SettingsHandler.getObject('tabs', [])
		currentOpenFiles = self.mainWindow.SettingsHandler.getSessionValue('openFiles', [])

		currentTabs[tabIndex]['textEditor'].fileReader.quit()
		#currentTabs[tabIndex]['textEditor'].thread.quit()

		currentTabs.remove(currentTabs[tabIndex])
		currentOpenFiles.remove(currentOpenFiles[tabIndex - 1])
		self.removeTab(tabIndex)

		self.mainWindow.SettingsHandler.setObject('tabs', currentTabs)
		self.mainWindow.SettingsHandler.setSessionValue('openFiles', currentOpenFiles)

class mainWindow(QMainWindow):

	def __init__(self):
		super().__init__()

		# Initialize the main window
		self.initialValues()

		applyTheme(self, relativePath(os.path.join('Themes')), 'darkTheme')
		loadFonts(relativePath(os.path.join('Fonts')))

		self.SettingsHandler = socketOS('Log Viewer')
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)

		# Set window properties
		# self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
		self.SettingsHandler.setValue('findTitle', 'Log Viewer - Finder')
		self.SettingsHandler.setValue('headerLabels', ['Log Content'])
		self.setWindowTitle(self.SettingsHandler.getValue('title'))
		self.setWindowSize()
		self.shortcuts()
		self.mainMenu()
		# self.titleBar = CustomTitleBar(self.menuBar, self)
		# self.setMenuWidget(self.titleBar)

		# Load Dock Widgets
		self.loadDockWidgets()

		# Load Components
		self.loadComponents()

	def error(self, code):
		self.popup = Popups.default(mainWindow=self.mainWindow)

		self.invalidExtension = self.popup.error(title="Invalid File Extension", message="Please choose a valid file.")

	def initialValues(self):
		self.logPath = None
		self.cleanRecentFiles = None
		self._pressed = False

	def setWindowSize(self):
		self.setMinimumSize(800, 800)
		defaultSizeX, defaultSizeY = self.SettingsHandler.getValue('sizeX', 800), self.SettingsHandler.getValue('sizeY',
																												800)
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
		self.tab = tabs(mainWindow=self)
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
		QShortcut(QKeySequence(Settings.logViewerSettings.shortcuts['openFileDialog']), self).activated.connect(
			self.chooseLogFile)
		QShortcut(QKeySequence(Settings.logViewerSettings.shortcuts['closeTab']), self).activated.connect(self.closeTab)
		QShortcut(QKeySequence(Settings.logViewerSettings.shortcuts['find']), self).activated.connect(
			self.showFindWidget)
		QShortcut(QKeySequence(Settings.logViewerSettings.shortcuts['wordWrap']), self).activated.connect(
			self.changeWordWrap)
		QShortcut(QKeySequence(Settings.logViewerSettings.shortcuts['themeSelector']), self).activated.connect(
			self.showThemeWidget)

	def closeTab(self):
		self.tab.onCloseEvent(self.tab.currentIndex())

	def chooseLogFile(self):
		try:
			if not self.isVisible():
				self.setVisible(False)

			self.selectedFile = openLogFileDialog(mainWindow=self).getSelectedFiles()

			if not self.selectedFile:
				self.error(400)

			if self.selectedFile is not None:
				if not self.isVisible():
					self.show()

				self.statusBar.showMessage(f'Loading {self.selectedFile}')
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

	def closeEvent(self, event=None):
		print('closing')
		self.SettingsHandler.saveConfig()
		self.tab.thread_pool.clear()
		self.tab.destroy()
		# self.destroy()
		QApplication.quit()

	def appendOpenFile(self, file: str):
		currentOpenedFiles = self.SettingsHandler.getSessionValue('openFiles', [])
		currentOpenedFiles.append(file)
		self.SettingsHandler.setSessionValue('openFiles', currentOpenedFiles)
		print(f'Currently Opened Files: %s' % currentOpenedFiles)
		self.appendMenuRecentFile(file)

	def appendMenuRecentFile(self, file: str):
		print(f'Currently Selected File: %s' % file)
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
