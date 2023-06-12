import os

from PyQt5.QtGui import QFontDatabase, QFont


def applyTheme(parent, themePath, selectedTheme):
	style = ''

	for file in os.listdir(os.path.join(themePath, selectedTheme)):
		if os.path.isfile(os.path.join(themePath, selectedTheme, file)):
			fullPath = os.path.join(themePath, selectedTheme, file)
			with open(fullPath) as themeFile:
				style += themeFile.read()

	parent.setStyleSheet(style)

def loadFonts(fontsPath):
	fontFamilies = []
	for font in os.listdir(fontsPath):
		font_id = QFontDatabase.addApplicationFont(os.path.join(fontsPath, font))
		if font_id != -1:
			fontFamilies.append(QFontDatabase.applicationFontFamilies(font_id)[0])

	return fontFamilies