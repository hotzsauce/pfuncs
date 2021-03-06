"""
module for Token, the basic lexeme object
"""
class Token(object):

	def __init__(
		self, 
		token_type, 
		value
	):
		self.type = token_type
		self.value = value

	def __str__(self):
		return '<{klass}({type}, {value})>'.format(
				klass=self.__class__.__name__,
				type=self.type,
				value=self.value
		)

	def __repr__(self):
		return self.__str__()