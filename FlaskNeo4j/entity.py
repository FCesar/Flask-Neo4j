import json

class MyEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__   

class Entity(object):

	id = 0

	def __init__(self, obj:dict):
		self.__dict__ = obj

	@classmethod
	def name(cls):
		return cls.__name__

	def __s(self):
		return json.dumps(self.__dict__,cls=MyEncoder)

	def json(self):
		return self.__s();

	