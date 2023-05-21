import hashlib

from datetime import datetime
from time import sleep

import os

import pandas as pd

from PyQt5.QtWidgets import QTextEdit

from System import recommendedRam

import psutil
from PyQt5.QtCore import QThread, pyqtSignal, QFile, QTextStream, QObject, QRunnable, pyqtSlot, QTimer
from PyQt5.QtGui import QTextCursor, QTextFormat

class appendTextThread(QThread):
	appendSignal = pyqtSignal(str)

	def __init__(self, editor, text):
		super().__init__()
		self.editor = editor
		self.text = text

	def run(self):
		self.appendSignal.emit(self.text)

	def appendText(self, text):
		#self.editor.moveCursor(QTextCursor.End)
		self.editor.appendText(text)

class fileReader(QThread):
	fileHasChanged = pyqtSignal(bool)
	reset = False
	def __init__(self, obj, parent, index, file):
		super().__init__()

		fileHasChanged = pyqtSignal(bool)

		# Generate a unique ID
		self.idComposition = bytes(str(str(file) + str(datetime.now()) + str(index)), 'utf-8')
		self.executionId = hashlib.sha256(self.idComposition).hexdigest()

		self.index = index
		self.parent = parent

		self.file = file
		self.fileSize = 0
		self.readSize = int()
		self.count = 0

		self.buffer = int((1024 * 1024) * 1024)

		self.object = obj

	def run(self):
		self.chunkAbsIndex = list()

		while self.isRunning():

			self.fileSize = os.stat(self.file).st_size

			if (self.fileSize != self.readSize and self.fileSize != 0) or (self.reset == True):
				self.stream = self.readFile()
				self.adaptiveBuffer()

				# File is Increasing:
				if self.fileSize > self.readSize:
					while not self.stream.atEnd():

						# File had not been read yet
						if self.object.pos == 0:

							print('Initializing')
							text = self.stream.read(self.buffer)
							self.object.pos = self.stream.pos()
							self.object.initialize(text)

						# File increased
						elif self.object.pos > 0:
							self.stream.seek(self.object.pos)
							self.object.write(self.stream.read(self.buffer))
							self.object.pos = self.stream.pos()

				# File has decreased:
				elif self.fileSize < self.readSize or self.reset:
					self.reset = False
					while not self.stream.atEnd():
						# Flush to clean QPlainTextEdit
						if self.stream.pos() == 0:
							print('Flushing')
							text = self.stream.read(self.buffer)
							self.object.pos = self.stream.pos()
							print(text)
							self.object.flushObject(text)

						# Write changes
						elif self.object.pos > 0:
							self.stream.seek(self.object.pos)
							self.object.write(self.stream.read(self.buffer))
							self.object.pos = self.stream.pos()

				print('File has been read successfully')

				self.readSize = self.fileSize

			else:
				if self.fileSize == 0 and self.object.pos > 0:
					self.object.flushObject(str())

				#sleep(2)

	def readFile(self):
		self.fileObject = QFile(self.file)
		self.fileContent = self.fileObject.open(QFile.ReadOnly)
		stream = QTextStream(self.fileObject)
		return stream

	def adaptiveBuffer(self):
		self.allocatedRam = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
		self.recommededBuffer = recommendedRam - self.allocatedRam
		self.buffer = abs(int((1024 * 1024) * self.recommededBuffer))

	def applyBlockSeparators(self):
		self.parent.blockSeparator = "<hr>"
		self.parent.textCursor().beginEditBlock()
		self.parent.textCursor().movePosition(QTextCursor.Start)
		while self.parent.textCursor().movePosition(QTextCursor.NextBlock):
			self.parent.textCursor().insertHtml(self.parent.blockSeparator)
		self.parent.textCursor().endEditBlock()


	@pyqtSlot()
	def objectMonitor(self):
		if self.object.text and not self.parent.processing:
			print("Object has Text" )
			self.fileHasChanged.emit(True)


	def setReset(self):
		print('Resetting')
		self.reset = True


class fileStreaming(QObject):
	flush = pyqtSignal(str)
	string = pyqtSignal(str)
	text = str()
	pos = 0
	processing = False

	textDataFrame = pd.DataFrame()

	def __init__(self, parent):
		super(fileStreaming, self).__init__()
		self.parent = parent

	@pyqtSlot()
	def write(self, text):
		self.textDataFrame
		self.text += text

	@pyqtSlot()
	def initialize(self, text):
		self.string.emit(text)

	@pyqtSlot()
	def flushObject(self, text):
		self.flush.emit(text)
