from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QTableView, QHeaderView, QTableWidgetItem

import numpy as np

class logModel(QAbstractTableModel):
    def __init__(self, data: list, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.headers = definitions.headerLabels
        self._data = data
        self.r = len(self._data)

    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data[index.row()])
        return None

    def addData(self, index, rows, content):
        self.beginInsertRows(QModelIndex(), index, index+rows-1)
        for each in content:
            self._data.append(each)
        self.endInsertRows()
        self.r = len(self._data)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]
            if orientation == Qt.Vertical:
                return section
        return QVariant()

class logTable(QTableView):
    def __init__(self):
        super().__init__()
        #self.setHorizontalHeaderItem(0, QTableWidgetItem(definitions.headerLabels))
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._scroll = True

    def beforeInsert(self):
        vbar = self.verticalScrollBar()
        self._scroll = vbar.value() == vbar.maximum()

    def afterInsert(self):
        if self._scroll:
            self.scrollToBottom()
