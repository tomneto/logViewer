import os
import time
from functools import partial
from itertools import count

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QFile, QTextStream, QObject, QTimer
from PyQt5.QtGui import QTextDocument
from more_itertools import divide

class logReader(QThread):

    outputSignal = pyqtSignal(QTextStream)

    def __init__(self, file, parent=None, index=0):
        super(QThread, self).__init__()
        self.Count = None
        self.index = index
        self.is_running = True
        self.file = file
        self.lastContentLength = 0
        self.fileSize = 0
        self.setParent(parent)
        self.id = None

    def run(self):
        self.id = 0
        while True:
            if self.fileSize < os.stat(self.file).st_size:
                #print(f"{self.fileSize} < {os.stat(self.file).st_size}")

                self.fileSize = os.stat(self.file).st_size

                self.stream = self.readFile()
                self.outputSignal.emit(self.stream)

                #print(f"Thread is emitting this > {self.content}")

            else:
                time.sleep(5)
            time.sleep(5)

    def readFile(self):
        self.contentLength = int()
        self.fileObject = QFile(self.file)
        self.fileObject.open(QFile.ReadOnly)
        stream = QTextStream(self.fileObject)
        return stream

    def stop(self):
        try:
            self.stream.readAll()
            self.isRunning = False
            self.blockSignals(True)
            self.yieldCurrentThread()
        except:
            print(f'Failed to stop thread {self.index}')

    def watch(self, tab):
        try:
            self.outputSignal.connect(
                partial(tab['textEditor'].updateContent, self.index))
            self.start()
            self.isRunning = True
            #self.finished.connect(
            #    partial(tab['textEditor'].updateContent, self.index))
        except:
            print(f'Failed to start thread {self.index}')

