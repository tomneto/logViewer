import sys

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QWidget, QLabel

class CustomTitleBar(QWidget):
	def __init__(self, mainMenu, parent):
		super().__init__(parent)

		self.setParent(parent)
		self.setMaximumHeight(50)
		self.setObjectName("customTitleBar")

		# Title label
		self.titleLabel = QLabel(self)
		self.titleLabel.setObjectName("titleLabel")
		self.titleLabel.setText(parent.windowTitle())
		self.titleLabel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
		self.titleLabel.setContentsMargins(0, 0, 0, 0)

		# Button container right
		self.buttonContainerRight = QWidget(self)
		self.buttonContainerRight.setObjectName("buttonContainerRight")
		self.buttonContainerRight.setContentsMargins(0, 0, 0, 0)

		# Button container left
		self.buttonContainerLeft = QWidget(self)
		self.buttonContainerLeft.setObjectName("buttonContainerLeft")
		self.buttonContainerLeft.setContentsMargins(0, 0, 0, 0)


		# Create Buttons Based on OS
		if sys.platform == 'darwin':
			print('Im on Mac OS X')
			self.minButton = QPushButton(self.buttonContainerLeft)
			self.maxButton = QPushButton(self.buttonContainerLeft)
			self.closeButton = QPushButton(self.buttonContainerLeft)

			self.buttonLayout = QHBoxLayout(self.buttonContainerLeft)
			self.buttonLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
			self.buttonLayout.setContentsMargins(0, 0, 0, 0)
		else:
			print('Im on Windows or Linux')
			self.minButton = QPushButton(self.buttonContainerRight)
			self.maxButton = QPushButton(self.buttonContainerRight)
			self.closeButton = QPushButton(self.buttonContainerRight)

			self.buttonLayout = QHBoxLayout(self.buttonContainerRight)
			self.buttonLayout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
			self.buttonLayout.setContentsMargins(0, 0, 0, 0)


		# Minimize button
		self.minButton.setText('-')
		self.minButton.setObjectName("minButton")
		#self.minButton.setIcon(QIcon("minimize.png"))
		self.minButton.setFixedSize(15, 15)
		self.minButton.clicked.connect(parent.showMinimized)

		# Maximize button
		self.maxButton.setObjectName("maxButton")
		#self.maxButton.setIcon(QIcon("maximize.png"))
		self.maxButton.setFixedSize(15, 15)
		self.maxButton.clicked.connect(self.toggleMaximized)

		# Close button
		self.closeButton.setText('x')
		self.closeButton.setObjectName("closeButton")
		#self.closeButton.setIcon(QIcon("close.png"))
		self.closeButton.setFixedSize(15, 15)
		self.closeButton.clicked.connect(parent.close)

		# Place Buttons Based on the OS
		if sys.platform == 'darwin':
			self.buttonLayout.addWidget(self.closeButton)
			self.buttonLayout.addWidget(self.minButton)
			self.buttonLayout.addWidget(self.maxButton)
		else:
			self.buttonLayout.addWidget(self.minButton)
			self.buttonLayout.addWidget(self.maxButton)
			self.buttonLayout.addWidget(self.closeButton)

		# Main layout
		mainLayout = QHBoxLayout(self)
		mainLayout.setContentsMargins(5, 5, 5, 5)
		mainLayout.addWidget(self.buttonContainerLeft)
		mainLayout.addWidget(self.titleLabel)
		mainLayout.addWidget(self.buttonContainerRight)
		mainLayout.addWidget(mainMenu())

		self.setMouseTracking(True)

	def toggleMaximized(self):
		if self.window().isMaximized():
			self.window().showNormal()
		else:
			self.window().showMaximized()

	def mousePressEvent(self, event):
		self.parent()._mouse_pos = event.pos()
		self.parent()._pressed = True
		# Determine the type of resize based on mouse position
		if self.parent()._mouse_pos.x() < 10:
			self.parent()._resize_type = "left"
		elif self.parent().width() - self.parent()._mouse_pos.x() < 10:
			self.parent()._resize_type = "right"
		elif self.parent()._mouse_pos.y() < 10:
			self.parent()._resize_type = "top"
		elif self.parent().height() - self.parent()._mouse_pos.y() < 10:
			self.parent()._resize_type = "bottom"
		else:
			self.parent()._resize_type = None
		if self.parent()._resize_type == "left" or self.parent()._resize_type == "right":
			self.parent().setCursor(Qt.SizeHorCursor)
		elif self.parent()._resize_type == "top" or self.parent()._resize_type == "bottom":
			self.parent().setCursor(Qt.SizeVerCursor)
		else:
			self.parent().setCursor(Qt.SizeAllCursor)

	def resizeEvent(self, event):
		currentX = event.size().height()
		currentY = event.size().width()

	def mouseMoveEvent(self, event):
		if not self.parent()._pressed:
			# Set the cursor type based on the mouse position
			if event.pos().x() < 10 or self.parent().width() - event.pos().x() < 10:
				self.parent().setCursor(Qt.SizeHorCursor)
			elif event.pos().y() < 10 or self.parent().height() - event.pos().y() < 10:
				self.parent().setCursor(Qt.SizeVerCursor)
			elif event.pos().y() < 100:
				self.parent().setCursor(Qt.ArrowCursor)
			else:
				self.parent().setCursor(Qt.SizeAllCursor)
			return
		delta = QPoint(event.pos() - self.parent()._mouse_pos)
		if self.parent()._resize_type == "left":
			self.parent().setGeometry(self.parent().x() + delta.x(), self.parent().y(), self.parent().width() - delta.x(), self.parent().height())
		elif self.parent()._resize_type == "right":
			new_width = max(self.parent().width() + delta.x() // 10, self.parent().minimumWidth())
			self.parent().setGeometry(self.parent().x(), self.parent().y(), new_width, self.parent().height())
		elif self.parent()._resize_type == "top":
			self.parent().setGeometry(self.parent().x(), self.parent().y() + delta.y(), self.parent().width(), self.parent().height() - delta.y())
		elif self.parent()._resize_type == "bottom":
			# self.parent().mousePosition = delta.y()
			# print(self.parent().mousePosition)
			new_height = max(self.parent().x(), self.parent().y() + delta.y(), self.parent().width(), self.parent().height() - delta.y())
			# max(self.parent().height() + delta.y() // 10, self.parent().minimumHeight())
			self.parent().setGeometry(self.parent().x(), self.parent().y(), self.parent().width(), new_height)
		else:
			self.parent().move(self.parent().pos() + delta)

	def mouseReleaseEvent(self, event):
		self.parent()._pressed = False
		self.parent()._resize_type = None
		self.parent().setCursor(Qt.ArrowCursor)

	def mouseDoubleClickEvent(self, event):
		if event.button() == Qt.LeftButton:
			if self.parent().isMaximized():
				self.parent().showNormal()
			else:
				self.parent().showMaximized()
			event.accept()
		else:
			super(CustomTitleBar, self).mouseDoubleClickEvent(event)
