from PyQt5.QtCore import QBasicTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QPushButton


class LoadingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.progress = QProgressBar(self)
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)

        layout.addWidget(self.progress)

        self.button = QPushButton('Start', self)
        self.button.clicked.connect(self.startLoading)

        layout.addWidget(self.button)

        self.setLayout(layout)

        self.timer = QBasicTimer()
        self.step = 0

    def timerEvent(self, event):
        if self.step >= 100:
            self.timer.stop()
            self.button.setText('Finished')
            return

        self.step += 1
        self.progress.setValue(self.step)

    def startLoading(self):
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText('Start')
        else:
            self.timer.start(100, self)
            self.button.setText('Stop')
