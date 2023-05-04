import os
import time
from functools import partial
from itertools import count

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QFile, QTextStream, QObject, QTimer, QRunnable, pyqtSlot, Qt
from PyQt5.QtGui import QTextDocument, QTextCursor, QCursor
from more_itertools import divide



class logReader(QRunnable):


    def __init__(self, obj, parent, index, file):
        super().__init__()
        self.index = index
        self.parent = parent

        self.file = file
        self.fileSize = 0

        self.object = obj

        self.buffer = 64000

    def run(self):
        print('running')
        self.overallContent = None
        while True:
            if self.fileSize < os.stat(self.file).st_size:
                print(f"if {self.fileSize} < {os.stat(self.file).st_size}")

                self.fileSize = os.stat(self.file).st_size

                self.stream = self.readFile()

1823hsdasx
                while not self.stream.atEnd():
                    self.currentContent = self.stream.readLine(maxLength=self.buffer)

                    self.object.appendText(str(self.currentContent))

                    print(f"Thread is emitting this > {self.currentContent}")

    def readFile(self):
        self.contentLength = int()
        self.fileObject = QFile(self.file)
        self.fileObject.open(QFile.ReadOnly)
        stream = QTextStream(self.fileObject)
        return stream


