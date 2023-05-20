

class logger:

	def __init__(self, obj=None, path=None, debug=False):
		self.obj = obj
		self.debug = debug
		self.path = path

	def add(self, text):
		if self.debug:
			print(text)

	def watch(self):
		while self.obj:
			print(f'Class {self.obj} Current State:')
			print(self.obj)