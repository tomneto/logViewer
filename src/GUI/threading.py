import time
from datetime import datetime
from time import sleep

import numpy as np
import os

from src.System import recommendedRam

import numpy as np
import psutil
from PyQt5.QtCore import QThread, pyqtSignal, QFile, QTextStream, QObject, QRunnable, pyqtSlot
from PyQt5.QtGui import QTextCursor

class appendThread(QThread):
	appendSignal = pyqtSignal(str)

	def __init__(self, editor, text):
		super().__init__()
		self.editor = editor
		self.text = text


	def run(self):
		self.appendSignal.emit(self.text)

	def appendText(self, text):
		self.editor.moveCursor(QTextCursor.End)
		self.editor.insertPlainText(text)

class fileReader(QThread):

	def __init__(self, obj, parent, index, file):
		super().__init__()
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

		while True:

			self.fileSize = os.stat(self.file).st_size

			if self.fileSize != self.readSize and self.fileSize != 0:
				self.count += 1
				print()
				print(f'================================================================ Execution: {self.count} at === {datetime.now()}')
				print()
				self.stream = self.readFile()
				self.adaptiveBuffer()

				print(f'Comparing File has Increasing : {self.readSize / 1000} > fileItself {self.fileSize / 1000}')
				print(f'Comparing File has decreased : {self.readSize / 1000} < fileItself {self.fileSize / 1000}')

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
				elif self.fileSize < self.readSize:
					while not self.stream.atEnd():
						# Flush to clean QPlainTextEdit
						if self.stream.pos() == 0:
							print('Flushing')
							text = self.stream.read(self.buffer)
							self.object.pos = self.stream.pos()
							self.object.flushObject(text)

						# Write changes
						elif self.object.pos > 0:
							self.stream.seek(self.object.pos)
							self.object.write(self.stream.read(self.buffer))
							self.object.pos = self.stream.pos()

				print(f'Setting Read Size {self.fileSize}')
				self.readSize = self.fileSize
			else:
				if self.fileSize == 0 and self.object.pos > 0:
					self.object.flushObject(str())

				sleep(1)

	def readFile(self):
		self.fileObject = QFile(self.file)
		self.fileContent = self.fileObject.open(QFile.ReadOnly)
		stream = QTextStream(self.fileObject)
		return stream

	def adaptiveBuffer(self):
		print()
		print(f'Buffer size once was: {self.buffer}')
		self.allocatedRam = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
		self.recommededBuffer = recommendedRam - self.allocatedRam
		self.buffer = abs(int((1024 * 1024) * self.recommededBuffer))
		print(f'Setting buffer size has changed: {self.buffer}')
		print()

class fileStreaming(QObject):
	flush = pyqtSignal(str)
	string = pyqtSignal(str)
	text = str()
	pos = 0
	processing = False

	def __init__(self, parent):
		super(fileStreaming, self).__init__()
		self.parent = parent

	@pyqtSlot()
	def write(self, text):
		self.text += text

	@pyqtSlot()
	def initialize(self, text):
		self.string.emit(text)

	@pyqtSlot()
	def flushObject(self, text):
		self.flush.emit(text)
