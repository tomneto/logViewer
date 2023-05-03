import json
import os

from PyQt5.QtCore import QSettings


#class socketIO:
#	def __init__(self, classSocket):
#		self.classSocket = classSocket
#
#	def load(self, path):
#		with open(os.path.join('/Volumes/Projetos/Git/Elemental/ElementalTools/SystemFiles/UserSettings/LogViewer/user.json'), 'r') as f:
#			configuration = json.loads(f.read())
#
#			for setting, default in self.classSocket.userSettings.items():
#				try:
#					self.classSocket.__setattr__(setting, configuration[setting])
#
#				except:
#					self.classSocket.__setattr__(setting, default)
#
#				print(self.classSocket.__getattribute__(setting))
#
#	def save(self, config):
#		with open(os.path.join('/Volumes/Projetos/Git/Elemental/ElementalTools/SystemFiles/UserSettings/LogViewer/user.json'), 'w') as f:
#			print(f'writing settings {config}')
#			f.write(config)
#

class socketIO:
    def __init__(self, applicationName):
        self.settings = QSettings("Elemental Tools", applicationName)
        self.settings.setValue('title', f'Elemental Tools - {applicationName}')

        self.objects = list()
        self.sessionValues = list()
        self.allAssignedValues = list()

    def setValue(self, key, value):
        #print(f'attempting to set stored value for {key}')
        self.allAssignedValues.append(value)

        if value != self.getValue(key):
            self.settings.setValue(key, value)
            #print(f'stored value for {key} is {value}')

    def getValue(self, key, default=None):
        #print(f'attempting to get stored value for {key}')
        storedValue = self.settings.value(key, default)
        #print(f'stored value obtained in {key} is {storedValue}')
        return storedValue

    def setObject(self, key, value):
        #print(f'attempting to set object value for {key}')
        for i, obj in enumerate(self.objects):
            if key in obj:
                self.objects[i] = {key: value}
                return

        self.objects.append({key: value})
        #print(f'assigned object for {key} is {value}')

    def getObject(self, key, default=None):
        #print(f'attempting to get object value for {key}')
        value = default
        for pyObject in self.objects:
            if key in pyObject:
                value = pyObject[key]
                break
        #print(f'assigned object in {key} is {value}')
        return value

    def setSessionValue(self, key, value):
        #print(f'attempting to set session value for {key}')
        for i, obj in enumerate(self.sessionValues):
            if key in obj:
                self.objects[i] = {key: value}
                return

        self.sessionValues.append({key: value})
        #print(f'assigned session value for {key} is {value}')

    def getSessionValue(self, key, default=None):
        #print(f'attempting to get session value for {key}')
        value = default
        for obj in self.sessionValues:
            if key in obj:
                value = obj[key]
                break
        #print(f'assigned session value in {key} is {value}')
        return value

    def saveConfig(self):
        for each in self.allAssignedValues:
            pass
            #print('setting found')
            #print(each)
        #self.settings.setValue('objects', json.dumps(self.objects))

class socketRequest:

    def __init__(self, url):
        self.url = url

