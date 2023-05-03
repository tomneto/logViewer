import json
import os

class settings:

	def __init__(self, name):
		self.name = name
		self.shortcuts = dict()


logViewerSettings = settings('logViewer')

logViewerSettings.shortcuts['openFileDialog'] = 'Ctrl+O'
logViewerSettings.shortcuts['closeTab'] = 'Ctrl+W'

logViewerSettings.shortcuts['find'] = 'Ctrl+F'
logViewerSettings.shortcuts['wordWrap'] = 'Ctrl+B'

logViewerSettings.shortcuts['themeSelector'] = 'Ctrl+Alt+C'