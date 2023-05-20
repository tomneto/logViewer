from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

from Settings import logViewerSettings

logViewerSettings.shortcuts['Open Log File'] = 'Ctrl+L'
logViewerSettings.shortcuts['Find'] = 'Ctrl+F'

def apply(parent):
	QShortcut(QKeySequence(logViewerSettings.shortcuts['Open Log File']), parent).activated.connect(
		parent.tab.homeOptions.showLogViewer)
	QShortcut(QKeySequence(logViewerSettings.shortcuts['Word Wrap']), parent).activated.connect(
		parent.tab.homeOptions.showLogViewer)
	#QShortcut(QKeySequence(logViewerSettings.shortcuts['Find']), parent).activated.connect(
	#	parent.tab.homeOptions.showLogViewer)
