import os, sys

import psutil
import platform

from PyQt5.QtCore import QSettings

availableRam = psutil.virtual_memory().total / (1024 ** 3)
recommendedRam = (availableRam / 32) * 1024
def osInfo():
	return platform.system()

class socketOS:
	def __init__(self, applicationName):
		self.settings = QSettings("Elemental Tools", applicationName)
		self.settings.setValue('title', f'Elemental Tools - {applicationName}')

		self.objects = list()
		self.sessionValues = list()
		self.allAssignedValues = list()

	def setValue(self, key, value):
		# print(f'attempting to set stored value for {key}')
		self.allAssignedValues.append(value)

		if value != self.getValue(key):
			self.settings.setValue(key, value)
			# print(f'stored value for {key} is {value}')

	def getValue(self, key, default=None):
		# print(f'attempting to get stored value for {key}')
		storedValue = self.settings.value(key, default)
		# print(f'stored value obtained in {key} is {storedValue}')
		return storedValue

	def setObject(self, key, value):
		# print(f'attempting to set object value for {key}')
		for i, obj in enumerate(self.objects):
			if key in obj:
				self.objects[i] = {key: value}
				return

		self.objects.append({key: value})
		# print(f'assigned object for {key} is {value}')

	def getObject(self, key, default=None):
		# print(f'attempting to get object value for {key}')
		value = default
		for pyObject in self.objects:
			if key in pyObject:
				value = pyObject[key]
				break
		# print(f'assigned object in {key} is {value}')
		return value

	def setSessionValue(self, key, value):
		# print(f'attempting to set session value for {key}')
		for i, obj in enumerate(self.sessionValues):
			if key in obj:
				self.objects[i] = {key: value}
				return

		self.sessionValues.append({key: value})
		# print(f'assigned session value for {key} is {value}')

	def getSessionValue(self, key, default=None):
		# print(f'attempting to get session value for {key}')
		value = default
		for obj in self.sessionValues:
			if key in obj:
				value = obj[key]
				break
		# print(f'assigned session value in {key} is {value}')
		return value

	def saveConfig(self):
		for each in self.allAssignedValues:
			pass
			# print('setting found')
			# print(each)
		# self.settings.setValue('objects', json.dumps(self.objects))


def relativePath(path):
	return os.path.join(os.path.dirname(sys.executable), path)


alreadyExists = list()
doesntExists = list()
def joinPath(*args):
	argList = [*args]

	print(f'Attempting to joinPath for {argList}')
	pathJoined = os.path.join(*args)

	if os.path.exists(pathJoined):
		alreadyExists.append(pathJoined)
	else:
		doesntExists.append(pathJoined)

	return pathJoined
