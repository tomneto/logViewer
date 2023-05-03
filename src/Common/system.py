import os
import platform
import sys

alreadyExists = list()
doesntExists = list()

def osInfo():
	return platform.system()

def relativePath(path):
	return os.path.join(os.path.dirname(sys.executable), path)

def joinPath(*args):
	argList = [*args]

	print(f'Attempting to joinPath for {argList}')
	pathJoined = os.path.join(*args)

	if os.path.exists(pathJoined):
		alreadyExists.append(pathJoined)
	else:
		doesntExists.append(pathJoined)

	return pathJoined
