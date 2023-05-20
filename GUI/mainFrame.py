import sys
from PyQt5.QtWidgets import QApplication, QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QPoint

class mainFrame(QFrame):
    def __init__(self, hostage, parent=None):
        super().__init__()

        # Set frame properties
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: lightblue")
        self._pressed = False
        self._resize_type = None
        self._mouse_pos = None

        # Add a label to the frame
        #label = QLabel('Hello, World!', self)
        #label.setAlignment(Qt.AlignCenter)

        # Set the layout of the frame
        layout = QVBoxLayout()
        layout.addWidget(hostage())

        self.setLayout(layout)

        self.setMouseTracking(True)
        self.parent().setMouseTracking(True)

        self.show()

    def mousePressEvent(self, event):
        self._mouse_pos = event.pos()
        self._pressed = True

        # Determine the type of resize based on mouse position
        if self._mouse_pos.x() < 30:
            self._resize_type = "left"
        elif self.width() - self._mouse_pos.x() < 30:
            self._resize_type = "right"
        elif self._mouse_pos.y() < 30:
            self._resize_type = "top"
        elif self.height() - self._mouse_pos.y() < 30:
            self._resize_type = "bottom"
        else:
            self._resize_type = None

        if self._resize_type == "left" or self._resize_type == "right":
            self.setCursor(Qt.SizeHorCursor)
        elif self._resize_type == "top" or self._resize_type == "bottom":
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.SizeAllCursor)

    def resizeEvent(self, event):
        currentX = event.size().height()
        currentY = event.size().width()

    def mouseMoveEvent(self, event):
        if not self._pressed:

            # Set the cursor type based on the mouse position
            if event.pos().x() < 10 or self.width() - event.pos().x() < 10:
                self.setCursor(Qt.SizeHorCursor)
            elif event.pos().y() < 10 or self.height() - event.pos().y() < 10:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.SizeAllCursor)
            return

        delta = QPoint(event.pos() - self._mouse_pos)
        if self._resize_type == "left":
            self.setGeometry(self.x() + delta.x(), self.y(), self.width() - delta.x(), self.height())
        elif self._resize_type == "right":
            new_width = max(self.width() + delta.x() // 10, self.minimumWidth())
            self.setGeometry(self.x(), self.y(), new_width, self.height())

        elif self._resize_type == "top":
            self.setGeometry(self.x(), self.y() + delta.y(), self.width(), self.height() - delta.y())
        elif self._resize_type == "bottom":
            #self.mousePosition = delta.y()
            #print(self.mousePosition)
            new_height = max(self.x(), self.y() + delta.y(), self.width(), self.height() - delta.y())
#max(self.height() + delta.y() // 10, self.minimumHeight())
            self.setGeometry(self.x(), self.y(), self.width(), new_height)

        else:
            self.move(self.pos() + delta)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self._resize_type = None
        self.setCursor(Qt.ArrowCursor)
