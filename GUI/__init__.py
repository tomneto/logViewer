import os
import os.path
from datetime import datetime

from PyQt5.QtCore import QSize, QThread
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QPixmap, QFont
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QMainWindow, QShortcut, QAction, QPushButton, QSizePolicy, QRadioButton, QLabel
from PyQt5.QtWidgets import QStatusBar, QApplication
from PyQt5.QtWidgets import QTabWidget, QWidget, QTabBar

from GUI.Widgets.progress import LoadingWidget
from System import socketOS
from System import relativePath

from Themes import applyTheme, loadFonts

from GUI import Popups, custom
from GUI.Dialogs import openFileDialog
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
		self.currentChanged.connect(self.changeTab)
		self.setUpdatesEnabled(True)
		self.tabCloseRequested.connect(self.onCloseEvent)

		self.thread = QThread()
		self.thread.start()


	def newTabButton(self, tab):
		if tab == 0:
			self.showOpenFileDialog()

	def showTab(self, index):
		print(f'Tab.showTab, initiate, %s' % datetime.now())
		#appendTabThread(self, index).start()
		currentTabs = self.mainWindow.SettingsHandler.getObject('tabs', [])
		filename = os.path.basename(currentTabs[index]['file'])
		self.addTab(currentTabs[index]['textEditor'], f'{filename}')
		self.setCurrentIndex(index)
		self.mainWindow.SettingsHandler.setObject('tabs', currentTabs)
		print(f'Tab.showTab, finished, %s' % datetime.now())

	def changeTab(self, currentPage):
		print('Change Tab')
		try:

			if currentPage != 0:

				currentTabs = self.mainWindow.SettingsHandler.getObject('tabs', [])

				for eachPage in currentTabs:
					if eachPage['id'] > 0 and eachPage['id'] != currentPage:
						print('Waiting')
						if eachPage['textEditor'].fileReader.isRunning(): eachPage['textEditor'].fileReader.exit(0)

					elif eachPage['id'] > 0 and eachPage['id'] == currentPage and not eachPage['textEditor'].fileReader.isRunning():
						print('Starting')
						#tempWidget = self.mainWindow.takeCentralWidget()
						#self.mainWindow.setCentralWidget(None)

						eachPage['textEditor'].fileReader.start()
						self.mainWindow.findWidget.changeFocus(eachPage['textEditor'])

						if self.mainWindow.SettingsHandler.getValue('realtime', True):
							eachPage['textEditor'].timer.start()

				self.mainWindow.SettingsHandler.setObject('tabs', currentTabs)
				self.mainWindow.SettingsHandler.setValue('selectedTableId', currentPage)


		except:
			raise Exception(f'Failed onChange to {currentPage}')

	def blankPage(self):
		blankWidget = QWidget()
		blankWidget.setObjectName('blankTab')

		self.mainWindow.SettingsHandler.setObject('logViewerHome', blankWidget)

		self.mainWindow.openFile('', blankWidget)

		self.addTab(blankWidget, '+')
		self.tabBar().setTabButton(0, QTabBar.LeftSide, None)
		self.tabBar().setTabButton(0, QTabBar.RightSide, None)

	def show(self):
		self.mainWindow.setCentralWidget(self.mainWindow.tab)

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

		applyTheme(self, relativePath(os.path.join('appThemes')), 'darkTheme')
		fontFamilies = loadFonts(os.path.join(relativePath('appThemes'), 'Fonts'))

		if fontFamilies:
			fontFamily = fontFamilies[0]
			print(f'Loading font family: {fontFamily}')
			font = QFont(fontFamily, 12)  # Set font size
			self.setFont(font)

		self.SettingsHandler = socketOS('Log Viewer')
		self.statusBar = QStatusBar()

		if self.SettingsHandler.getValue('realtime', True):
			self.togglePixmap = QPixmap(relativePath('appThemes/darkTheme/resources/toggle/on.png'))
		else:
			self.togglePixmap = QPixmap(relativePath('appThemes/darkTheme/resources/toggle/off.png'))

		self.realtimeSlide = QLabel()
		self.realtimeLabel = QLabel('Realtime Rendering: ')
		self.realtimeSlide.setObjectName("realtimeRenderSlide")
		self.realtimeSlide.setPixmap(self.togglePixmap)
		self.realtimeSlide.mousePressEvent = self.toggleRealtime

		self.statusBar.layout().addWidget(self.realtimeLabel)
		self.statusBar.layout().addWidget(self.realtimeSlide)

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

	def openFile(self, file: str, widget=None):
		try:
			currentTabs = self.SettingsHandler.getObject('tabs', [])

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
				newPage['textEditor'] = textEditor.QCodeEditor(mainWindow=self, index=currentId, file=file, pageData=newPage, parent=self.tab)

			currentTabs.append(newPage)

			self.SettingsHandler.setObject('tabs', currentTabs)
			print(f'mainWindow.openFile initial %s' % datetime.now())
			self.tab.showTab(currentId)
			print(f'mainWindow.openFile finished %s' % datetime.now())

		except:
			pass

	def toggleRealtime(self, event):
		if event.buttons() == Qt.LeftButton:
			if self.SettingsHandler.getValue('realtime', True):
				self.SettingsHandler.setValue('realtime', False)
				[e['textEditor'].timer.stop() for e in self.SettingsHandler.getObject('tabs', []) if e['id'] > 0]
				self.togglePixmap = QPixmap(relativePath('appThemes/darkTheme/resources/toggle/off.png'))
				self.realtimeSlide.setPixmap(self.togglePixmap)
			else:
				self.SettingsHandler.setValue('realtime', True)
				[e['textEditor'].timer.start() for e in self.SettingsHandler.getObject('tabs', []) if e['id'] > 0]
				self.togglePixmap = QPixmap(relativePath('appThemes/darkTheme/resources/toggle/on.png'))
				self.realtimeSlide.setPixmap(self.togglePixmap)

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

		self.themeWidget = themeWidget(self.SettingsHandler, parent=self)
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
			uniqueRecentFiles = set(self.SettingsHandler.getValue('recentFiles'))
			for each in uniqueRecentFiles:
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

			self.selectedFile = openFileDialog(mainWindow=self, fileExt="All Files (*);;Log Files (*.log)", title='Choose a Log File').getSelectedFiles()

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
		currentOpenedFiles = self.SettingsHandler.getSessionValue('openFiles', [])

		if filepath not in currentOpenedFiles:
			currentOpenedFiles.append(filepath)

			self.SettingsHandler.setSessionValue('openFiles', currentOpenedFiles)
			print(f'Currently Opened Files: %s' % currentOpenedFiles)
			self.appendMenuRecentFile(filepath)

			self.openFile(filepath)

	def closeEvent(self, event=None):
		print('closing')
		self.SettingsHandler.saveConfig()
		self.tab.thread_pool.clear()
		self.tab.destroy()
		# self.destroy()
		QApplication.quit()

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
