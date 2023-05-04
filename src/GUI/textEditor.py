import os
import sys
from ctypes import Union
from datetime import time, datetime

import numpy as np
from PyQt5.QtCore import Qt, QRect, QSize, QFile, QTextStream, QPoint, pyqtSlot
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QTextEdit
from PyQt5.QtGui import QColor, QPainter, QTextFormat, QTextDocument, QTextOption, QTextBlockFormat, QTextBlock, \
    QTextCursor, QTextCharFormat


class QLineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class QCodeEditor(QPlainTextEdit):
    def __init__(self, mainWindow, parent=None):
        super().__init__(parent)
        self.mainWindow = mainWindow

        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        self.lineColor = QColor(Qt.gray).lighter(160)
        self.textColor = QColor(Qt.black).lighter(160)

        self.defaultFormat = self.textCursor().blockFormat()
        self.defaultTextFormat = self.textCursor().charFormat()

        self.lineNumberArea = QLineNumberArea(self)
        self.document().blockCountChanged.connect(self.onBlockCountChanged)

        self.updateLineNumberAreaWidth(0)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.timestamp = datetime.now()
        self.timesThatTextChanged = 1

        self.updateRequest.connect(self.updateLineNumberArea)




        #self.textChanged.connect(self.resizeEvent)



    def textHook(self):
        if self.timesThatTextChanged > 0:
            print(f'Text Changing Timeout is {datetime.now() - self.timestamp}')
        self.timesThatTextChanged += 1

    def onBlockCountChanged(self, newBlockCount):
        self.count = newBlockCount
        self.applyBlockSeparators()
        self.updateLineNumberAreaWidth(self.count)
        #for pattern in self.loadUserTemplate()['patterns']:
        #    self.highlightInEditor(pattern['pattern'], pattern['backgroundColorHex'], pattern['textColorHex'],
        #                           pattern['caseSensitive'], self.)

    def applyBlockSeparators(self):
        self.blockSeparator = "<hr>"
        self.textCursor().beginEditBlock()
        self.textCursor().movePosition(QTextCursor.Start)
        while self.textCursor().movePosition(QTextCursor.NextBlock):
            self.textCursor().insertHtml(self.blockSeparator)
        self.textCursor().endEditBlock()

    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.document().blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.document().setDocumentMargin(0)
        self.setViewportMargins(self.lineNumberAreaWidth()+10, 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        #else:
        #    self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        #if rect.contains(self.viewport().rect()):
        #    self.updateLineNumberAreaWidth(0)

    def finishedDocument(self):
        self.setDocument(self.document())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        selection = QTextEdit.ExtraSelection()

        selection.format.setBackground(self.lineColor)
        selection.format.setForeground(self.textColor)

        selection.format.setProperty(QTextFormat.FullWidthSelection, False)

        self.textCursor().clearSelection()
        extraSelections.append(selection)
        if self.mainWindow.statusBar is not None:
            self.mainWindow.statusBar.showMessage(f"Total Count: {self.document().blockCount()} - Selected Line: {self.textCursor().blockNumber()+1} - Selection Length: {abs(self.textCursor().selectionStart() - self.textCursor().selectionEnd())}")
        self.setExtraSelections(extraSelections)

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
                self.highlightInEditor(pattern['pattern'], pattern['backgroundColorHex'], pattern['textColorHex'], pattern['caseSensitive'])

        self.setTextCursor(userCursorPosition)
        print(f'applyUserTemplate Timeout is {datetime.now() - startTimestamp}')

