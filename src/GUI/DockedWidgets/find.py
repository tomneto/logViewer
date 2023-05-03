from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget, QGridLayout, QFrame, QPushButton, QTextEdit, QCheckBox, QLabel

class findWidget(QDockWidget):

	def __init__(self, *args):
		super().__init__()
		self.setWindowTitle('Find')
		self.setBaseSize(50, 100)
		self.findItems = QFrame()
		self.findItems.layout = QGridLayout()

		self.leftFrame = QFrame()

		self.rightFrame = QFrame()

		self.caseSensitive = QCheckBox()
		self.caseSensitive.setText('Case Sensitive')
		self.findItems.layout.addWidget(self.caseSensitive, 0, 0)

		self.inputText = QTextEdit()
		self.findItems.layout.addWidget(self.inputText, 1, 0, 1, 0)

		self.resultCount = QLabel()
		self.resultCount.setAlignment(Qt.AlignRight)
		self.findItems.layout.addWidget(self.resultCount, 0, 3)

		self.goToPrevious = QPushButton()
		self.goToPrevious.setText('Previous')
		self.findItems.layout.addWidget(self.goToPrevious, 2, 0)

		self.goToNext = QPushButton()
		self.goToNext.setText('Next')
		self.findItems.layout.addWidget(self.goToNext, 2, 3)
		self.findItems.setLayout(self.findItems.layout)

		self.findItems.show()
		self.setWidget(self.findItems)

	def changeFocus(self, widget):
		self.widget = widget
		self.goToNext.disconnect()
		self.goToPrevious.disconnect()
		self.goToNext.clicked.connect(partial(self.widget.findInEditor, finder=self, direction='forward'))
		self.goToPrevious.clicked.connect(partial(self.widget.findInEditor, finder=self, direction='backward'))
