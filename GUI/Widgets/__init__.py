from datetime import datetime

from PyQt5.QtCore import QRect, QSize, QThread
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPainter, QTextFormat, QTextOption
from PyQt5.QtGui import QTextDocument, QTextCursor
from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit
from PyQt5.QtWidgets import QWidget

from GUI.Thread import fileStreaming, appendTextThread, fileReader


#class lineNumberAreaResizer(QThread):
#	def __init__(self)


class textEditor:

	class QCodeEditor(QPlainTextEdit):
		count = -1
		processing = False

		class QLineNumberArea(QWidget):
			def __init__(self, editor):
				super().__init__(editor)
				self.codeEditor = editor

			def sizeHint(self):
				return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

			def paintEvent(self, event):
				self.codeEditor.lineNumberAreaPaintEvent(event)

		def __init__(self, mainWindow, index, file, pageData, parent=None):
			print("Initializing QCodeEditor")
			super().__init__(parent)
			self.mainWindow = mainWindow
			self.parent = parent
			
			self.thread = QThread()

			self.thread.moveToThread(self.parent.thread)

			self.setReadOnly(True)
			self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

			self.lineColor = QColor(Qt.gray).lighter(160)
			self.textColor = QColor(Qt.black).lighter(160)

			self.defaultFormat = self.textCursor().blockFormat()
			self.defaultTextFormat = self.textCursor().charFormat()

			self.lineNumberArea = self.QLineNumberArea(self)

			self.timestamp = datetime.now()
			self.timesThatTextChanged = 1

			print("Creating Editor Object")
			self.object = fileStreaming(self)
			self.object.moveToThread(self.thread)

			print("Connecting to Initializing")
			self.object.string.connect(self.initialize)

			print("Connecting to Cleaning")
			self.object.flush.connect(self.flush)

			print("Creating Editor Thread")
			self.fileReader = fileReader(obj=self.object, parent=self, index=index, file=file)
			self.fileReader.fileHasChanged.connect(self.onObjChange)
			self.fileReader.moveToThread(self.thread)

			self.timer = QTimer()
			self.timer.timeout.connect(lambda: self.fileReader.objectMonitor())

			self.updateLineNumberAreaWidth(0)
		# Text Editor Threading
		def onObjChange(self, hasChanged):
			print(f"onObjChange {hasChanged}")
			if hasChanged and not self.processing:
				text = self.object.text
				self.object.text = str()
				self.processing = True
				self.textAppendThread.appendText(text)
				self.processing = False

		def appendText(self, text):
			if not self.processing:
				self.processing = True
				#doc = QTextDocument(self.document().toPlainText() + text)
				#self.setDocument(doc)
				self.selection = self.extraSelections()
				self.cursorPosition = self.textCursor().position()
				self.moveCursor(QTextCursor.End)
				self.insertPlainText(text)
				self.moveCursor(self.cursorPosition)
				self.setExtraSelections(self.selection)
				self.processing = False

		def initialize(self, text):
			if not self.processing:
				self.processing = True
				self.textAppendThread = appendTextThread(self, text)
				self.textAppendThread.moveToThread(self.thread)
				self.textAppendThread.appendSignal.connect(self.appendText)
				self.textAppendThread.start()
				self.updateRequest.connect(self.updateLineNumberArea)
				self.blockCountChanged.connect(self.onBlockCountChanged)
				self.cursorPositionChanged.connect(self.highlightCurrentLine)
				self.timer.start(3000)
				self.processing = False

		def onBlockCountChanged(self, newBlockCount):
			self.parent.count = newBlockCount
			self.applyBlockSeparators()
			self.updateLineNumberAreaWidth(self.count)

		def highlightCurrentLine(self):
			extraSelections = []
			selection = QTextEdit.ExtraSelection()

			selection.format.setBackground(self.lineColor)
			selection.format.setForeground(self.textColor)

			selection.format.setProperty(QTextFormat.FullWidthSelection, False)

			self.textCursor().clearSelection()
			extraSelections.append(selection)
			if self.mainWindow.statusBar is not None:
				self.mainWindow.statusBar.showMessage(
					f"Total Count: {self.document().blockCount()} - Selected Line: {self.textCursor().blockNumber() + 1} - Selection Length: {abs(self.textCursor().selectionStart() - self.textCursor().selectionEnd())}")
			self.setExtraSelections(extraSelections)
		def flush(self, text):
			if not self.processing:
				self.processing = True
				self.setPlainText(str())
				self.textAppendThread.exit(0)
				self.initialize(text)
				self.processing = False

		# Text Editor Behaviour
		def textHook(self):
			if self.timesThatTextChanged > 0:
				print(f'Text Changing Timeout is {datetime.now() - self.timestamp}')
			self.timesThatTextChanged += 1

		def updateLineNumberArea(self, rect, dy):
			if not self.processing:
				self.processing = True
				if dy:
					self.lineNumberArea.scroll(0, dy)
				self.processing = False
				#else:
			#	self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
			#if rect.contains(self.viewport().rect()):
			#	self.updateLineNumberAreaWidth(0)

		def applyBlockSeparators(self):
			self.blockSeparator = "<hr>"
			self.textCursor().beginEditBlock()
			self.textCursor().movePosition(QTextCursor.Start)
			while self.textCursor().movePosition(QTextCursor.NextBlock):
				self.textCursor().insertHtml(self.blockSeparator)
			self.textCursor().endEditBlock()

		def updateLineNumberAreaWidth(self, _):
			self.document().setDocumentMargin(0)
			self.setViewportMargins(self.lineNumberAreaWidth() + 10, 0, 0, 0)



		# for pattern in self.loadUserTemplate()['patterns']:
		#    self.highlightInEditor(pattern['pattern'], pattern['backgroundColorHex'], pattern['textColorHex'],
		#                           pattern['caseSensitive'], self.)

		def lineNumberAreaWidth(self):
			digits = 1
			max_value = max(1, self.document().blockCount())
			while max_value >= 10:
				max_value /= 10
				digits += 1
			space = 3 + self.fontMetrics().width('9') * digits
			return space

		def resizeEvent(self, event):
			if not self.processing:
				super().resizeEvent(event)
				cr = self.contentsRect()
				self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

		def lineNumberAreaPaintEvent(self, event):

			self.setDocument(self.document())
			painter = QPainter(self.lineNumberArea)

			painter.fillRect(event.rect(), Qt.lightGray)
			block = self.firstVisibleBlock()
			blockNumber = block.blockNumber()
			top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
			bottom = top + self.blockBoundingRect(block).height()

			height = self.fontMetrics().height()
			#
			while block.isValid() and (top <= event.rect().bottom()):

				if block.isVisible() and (bottom >= event.rect().top()):
					number = str(blockNumber + 1)
					painter.setPen(Qt.black)
					painter.drawText(0, int(top), self.lineNumberArea.width(), height, Qt.AlignRight, number)
					painter.drawLine(0, int(bottom), self.lineNumberArea.width(), int(bottom))

				block = block.next()
				top = bottom
				bottom = top + self.blockBoundingRect(block).height()
				blockNumber += 1

		def findInEditor(self, finder, direction: str):

			resultCount = 0
			input = finder.inputText.toPlainText()

			# Search settings:
			caseSensitiveCheck = finder.caseSensitive.isChecked()

			# Start Search
			if input != '':

				if direction == 'backward':
					flag = QTextDocument.FindBackward
					if caseSensitiveCheck:
						self.find(input, QTextDocument.FindCaseSensitively)
					else:
						self.find(input, flag)
				else:
					if caseSensitiveCheck:
						self.find(input, QTextDocument.FindCaseSensitively)
					else:
						self.find(input)

		def changeWordWrap(self):
			if self.mainWindow.SettingsHandler.getValue('wordWrapState'):
				self.setWordWrapMode(QTextOption.NoWrap)
			else:
				self.setWordWrapMode(QTextOption.WrapAnywhere)

		def highlightInEditor(self, pattern: str, bgcolor: hex, fgcolor: hex, caseSensitive: bool, selection=None):
			if selection is None:
				selection = self.textCursor()
			else:
				pass

			if caseSensitive:
				find = self.find(pattern, QTextDocument.FindCaseSensitively)
			else:
				find = self.find(pattern)

			if find:
				textColor = QColor(fgcolor)
				lineColor = QColor(bgcolor)
				currentFormat = selection.blockFormat()
				currentTextFormat = selection.charFormat()
				currentFormat.setBackground(lineColor)
				currentTextFormat.setForeground(textColor)
				selection.setBlockFormat(currentFormat)
				selection.setCharFormat(currentTextFormat)
			else:
				selection.setBlockFormat(self.defaultFormat)
				selection.setCharFormat(self.defaultTextFormat)

		def loadUserTemplate(self):
			self.setDocument(self.document())
			self.selectedTemplate = self.mainWindow.SettingsHandler.getValue('UserSelectedTemplate')
			self.userTemplates = self.mainWindow.SettingsHandler.getValue('Templates')
			for template in self.userTemplates:
				if template['title'] == self.selectedTemplate:
					self.userTemplate = template
					return self.userTemplate

		def applyUserTemplate(self):
			self.loadUserTemplate()
			self.setDocument(self.document())
			userCursorPosition = self.textCursor()
			startTimestamp = datetime.now()
			for eachBlock in range(self.blockCount()):
				for pattern in self.userTemplate['patterns']:
					self.highlightInEditor(pattern['pattern'], pattern['backgroundColorHex'], pattern['textColorHex'],
										   pattern['caseSensitive'])

			self.setTextCursor(userCursorPosition)
			print(f'applyUserTemplate Timeout is {datetime.now() - startTimestamp}')

