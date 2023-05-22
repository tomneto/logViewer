import json
import random

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QTableWidget, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem, QHeaderView, QPushButton, QComboBox, QLabel, QSizePolicy, QColorDialog, QLineEdit, QAction, QMenu
)
from PyQt5.QtGui import QColor

from GUI import Dialogs


class themeTableWidget(QTableWidget):

    def calculate_contrast_ratio(self, color1, color2):
        # Relative luminance calculation for sRGB color space
        def relative_luminance(color):
            r, g, b, _ = color.getRgbF()
            r = adjust_gamma(r)
            g = adjust_gamma(g)
            b = adjust_gamma(b)
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        # Gamma adjustment for sRGB color space
        def adjust_gamma(value):
            if value <= 0.03928:
                return value / 12.92
            else:
                return ((value + 0.055) / 1.055) ** 2.4

        # Calculate relative luminance for both colors
        luminance1 = relative_luminance(color1)
        luminance2 = relative_luminance(color2)

        # Calculate contrast ratio
        contrast_ratio = (luminance1 + 0.05) / (luminance2 + 0.05)
        return contrast_ratio

    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['Case Sensitive', 'Pattern', 'Background Color', 'Text Color'])
        self.rightClickMenu()

        self.itemChanged.connect(self.adaptiveContrast)

    def removeItem(self):
        selected_rows = self.selectedIndexes()
        for index in selected_rows:
            self.removeRow(index.row())

    def contextMenuEvent(self, event):
        global_pos = self.mapToGlobal(event.pos())
        self.showRightClickMenu.exec_(global_pos)

    def rightClickMenu(self):
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self.removeItem)
        self.showRightClickMenu = QMenu(self)
        self.showRightClickMenu.addAction(remove_action)

    def adaptiveContrast(self, item):
        if self.calculate_contrast_ratio(item.background().color(), item.foreground().color()) > 5:
            item.setForeground(item.foreground().color().darker())

class themeWidget(QDockWidget):
    def __init__(self, settingsHandler, parent=None):
        super().__init__(parent)
        self.SettingsHandler = settingsHandler
        self.private = True

        self.setWindowTitle("Color Templates")
        self.setMinimumSize(350, 350)

        # Create widgets
        self.table = themeTableWidget()
        self.table.cellDoubleClicked.connect(self.showColorSelector)
        self.table.cellChanged.connect(self.applyManualChangeColor)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.applyMainElements()

        self.loadComboboxValues()



    def applyMainElements(self):
        self.themeLabel = QLabel("Theme: ")

        self.titleLabel = QLabel("Title: ")
        self.titleValue = QLineEdit()
        self.titleValue.setEnabled(False)
        self.newTemplateButton = QPushButton("New Theme")
        self.newTemplateButton.setObjectName("newTemplateButton")
        self.newTemplateButton.clicked.connect(self.createNewTheme)

        self.comboBox = QComboBox()
        self.comboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.comboBox.currentTextChanged.connect(self.loadTableValues)

        self.loadThemesButton = QPushButton("Reload")
        self.loadThemesButton.setObjectName("loadButton")
        self.loadThemesButton.setMinimumSize(10, 10)
        self.loadThemesButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.loadThemesButton.clicked.connect(self.loadComboboxValues)

        self.addButton = QPushButton("+")
        self.addButton.setObjectName("addButton")
        self.addButton.clicked.connect(self.addRow)

        self.removeButton = QPushButton("-")
        self.removeButton.setObjectName("removeButton")
        self.removeButton.clicked.connect(self.table.removeItem)

        self.saveButton = QPushButton("Save Theme")
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.saveButton.clicked.connect(self.saveTableValues)

        self.exportButton = QPushButton("Export Theme")
        self.exportButton.setObjectName("exportButton")
        self.exportButton.clicked.connect(self.exportTableValues)

        self.importButton = QPushButton("Import Theme")
        self.importButton.setObjectName("importButton")
        self.importButton.clicked.connect(self.importTableValues)

        # Create layout
        self.mainLayout = QVBoxLayout()

        self.headerLayout = QHBoxLayout()
        self.headerLayout.addWidget(self.newTemplateButton)
        self.mainLayout.addLayout(self.headerLayout)

        self.themePropertiesLayout = QHBoxLayout()
        self.themePropertiesLayout.addWidget(self.titleLabel)
        self.themePropertiesLayout.addWidget(self.titleValue)
        self.themePropertiesLayout.addWidget(self.saveButton)
        self.mainLayout.addLayout(self.themePropertiesLayout)

        self.topLayout = QHBoxLayout()

        self.topLayout.addWidget(self.themeLabel)
        self.topLayout.addWidget(self.comboBox)
        self.topLayout.addWidget(self.loadThemesButton)

        self.mainLayout.addLayout(self.topLayout)

        self.mainLayout.addWidget(self.table)

        self.tableControllerLayout = QHBoxLayout()
        self.tableControllerLayout.addWidget(self.addButton)
        self.tableControllerLayout.addWidget(self.removeButton)

        self.mainLayout.addLayout(self.tableControllerLayout)

        self.jsonControllerLayout = QHBoxLayout()
        self.jsonControllerLayout.addWidget(self.importButton)
        self.jsonControllerLayout.addWidget(self.exportButton)

        self.mainLayout.addLayout(self.jsonControllerLayout)

        widget = QWidget()
        widget.setLayout(self.mainLayout)

        self.setWidget(widget)

    def createNewTheme(self):
        if not self.titleValue.isEnabled():
            #self.saveTableValues()
            self.table.clearContents()
            self.table.setRowCount(0)
            self.titleValue.setEnabled(True)
            self.titleValue.setText(f'{self.titleValue.text()}{random.randint(0, 2000)}')
            self.newTemplateButton.setEnabled(True)

    def loadComboboxValues(self):
        self.nemTemplateTitle = str(self.titleValue.text())

        self.comboBox.clear()
        userTemplates = self.SettingsHandler.getValue('Templates', [])
        for theme in userTemplates:
            self.comboBox.addItem(theme['title'])

        self.currentTemplateTitle = self.comboBox.currentText()
        self.SettingsHandler.setValue('UserSelectedTemplate', self.currentTemplateTitle)

        self.comboBox.setCurrentText(self.nemTemplateTitle)

    def loadTableValues(self):

        self.titleValue.setText(self.comboBox.currentText())
        userTemplates = self.SettingsHandler.getValue('Templates', [])

        try:
            for e in userTemplates:
                if e["title"] == self.comboBox.currentText():
                    self.title = e["title"]
                    for rowIdx, rowData in enumerate(e["patterns"]):
                        self.table.setRowCount(rowIdx+1)

                        caseSensitiveItem = QTableWidgetItem()
                        caseSensitiveItem.setTextAlignment(Qt.AlignCenter)
                        caseSensitiveItem.setCheckState(2 if rowData["caseSensitive"] else 0)
                        caseSensitiveItem.setFlags(caseSensitiveItem.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(rowIdx, 0, caseSensitiveItem)

                        patternItem = QTableWidgetItem(rowData["pattern"])
                        patternItem.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(rowIdx, 1, patternItem)

                        backgroundColorHexItem = QTableWidgetItem(rowData["backgroundColorHex"])
                        backgroundColorHexItem.setBackground(QColor(rowData["backgroundColorHex"]))
                        backgroundColorHexItem.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(rowIdx, 2, backgroundColorHexItem)

                        textColorHexItem = QTableWidgetItem(rowData["textColorHex"])
                        textColorHexItem.setBackground(QColor(rowData["textColorHex"]))
                        textColorHexItem.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(rowIdx, 3, textColorHexItem)

                    userData = None
                    self.table.resizeColumnsToContents()
                    self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                else:
                    error_message = "Invalid Theme File"

        except:
            error_message = "Invalid Theme Path"

    def saveTableValues(self):
        self.title = str(self.titleValue.text())
        userTemplates = self.SettingsHandler.getValue('Templates', [])
        print(userTemplates)

        template = dict()
        template["title"] = self.title
        template["private"] = self.private
        template["patterns"] = []

        for rowIdx in range(self.table.rowCount()):
            caseSensitiveItem = self.table.item(rowIdx, 0)
            patternItem = self.table.item(rowIdx, 1)
            backgroundColorHexItem = self.table.item(rowIdx, 2)
            textColorHexItem = self.table.item(rowIdx, 3)
            template["patterns"].append({
                "caseSensitive": True if caseSensitiveItem.checkState() else False,
                "pattern": patternItem.text(),
                "style": f"""color:{textColorHexItem.text().replace('"','')}; background-color:{backgroundColorHexItem.text().replace('"','')}""",
                "backgroundColorHex": backgroundColorHexItem.text(),
                "textColorHex": textColorHexItem.text(),
            })

        for e in userTemplates:
            if e["title"] == self.comboBox.currentText():
                userTemplates.remove(e)

        userTemplates.append(template)

        self.SettingsHandler.setValue('Templates', userTemplates)
        self.titleValue.setEnabled(False)
        self.loadComboboxValues()
        try:
            currentTable = self.SettingsHandler.getValue('selectedTableId')
            if currentTable != 0 and currentTable is not None:
                print('Applying User Template')
                print(self.SettingsHandler.getObject('tabs')[currentTable])
                self.SettingsHandler.getObject('tabs')[currentTable]['textEditor'].fileReader.setReset()
        except:
            pass
    def exportTableValues(self):

        userSelectedTemplate = [e for e in self.SettingsHandler.getValue('Templates', []) if e['title'] == self.SettingsHandler.getValue('UserSelectedTemplate', '')]
        print(userSelectedTemplate)
        Dialogs.saveFileDialog(mainWindow=self.parent, title='Choose Template Destination', fileExt='Template File (*.json)',
                               content=json.dumps(userSelectedTemplate[0], indent=2), latestDirectory=f"{self.SettingsHandler.getValue('latestSaveFileDir', '')}")
        print('export')

    def importTableValues(self):
        print('import')

    def showColorSelector(self, row, column):
        if column > 1:
            # Show color selector dialog and set selected color's hex value in "Color Hex" column
            colorDialog = QColorDialog(self)
            colorDialog.setOption(QColorDialog.ShowAlphaChannel, True)
            current_color_hex = self.table.item(row, column).text()
            current_color = QColor(current_color_hex)
            if current_color.isValid():
                colorDialog.setCurrentColor(current_color)

            if colorDialog.exec():
                color = colorDialog.selectedColor()
                hexColor = color.name(QColor.HexArgb)
                self.table.setItem(row, column, QTableWidgetItem(hexColor))
                backgroundColorHexItem = self.table.item(row, column)
                backgroundColorHexItem.setForeground(QColor(hexColor))
                row = self.table.currentRow()
                self.table.setItem(row, column, QTableWidgetItem(hexColor))
                self.table.item(row, column).setBackground(QColor(hexColor))

    def applyManualChangeColor(self, row, column):
        self.table.item(row, column).setTextAlignment(Qt.AlignCenter)
        if column > 1:
            self.table.item(row, column).setBackground(QColor(self.table.item(row, column).text()))

    def addRow(self):
        # Insert a new row with the same data
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        lastRow = self.table.rowCount() - 1

        patternItem = QTableWidgetItem(self.table.item(lastRow, 1))

        caseSensitiveItem = QTableWidgetItem()
        caseSensitiveItem.setTextAlignment(Qt.AlignCenter)
        caseSensitiveItem.setCheckState(0)
        caseSensitiveItem.setFlags(caseSensitiveItem.flags() & ~Qt.ItemIsEditable)

        backgroundColorHexItem = QTableWidgetItem('#ffffffff')
        textColorHexItem = QTableWidgetItem('#ffffffff')
        backgroundColorHexItem.setTextAlignment(Qt.AlignCenter)
        textColorHexItem.setTextAlignment(Qt.AlignCenter)
        patternItem.setTextAlignment(Qt.AlignCenter)

        self.table.setItem(row_position, 0, caseSensitiveItem)
        self.table.setItem(row_position, 1, patternItem)
        self.table.setItem(row_position, 2, backgroundColorHexItem)
        self.table.setItem(row_position, 3, textColorHexItem)
