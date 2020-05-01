
from pfuncs.lexer import Lexer

from pfuncs.functions import (
	Parser,
	Interpreter
)


def call(text):
	lexer = Lexer(text)
	parser = Parser(lexer)

	tree = parser.parse()
	interpreter = Interpreter(tree)

	return interpreter.interpret()

class Caller(object):

	def __init__(self, text):
		self.lexer = Lexer(text)
		self.parser = Parser(self.lexer)

	def call(self):
		tree = self.tree
		self.interpreter = Interpreter(tree)
		return self.interpreter.interpret()

	def summarize_tokens(self):
		for t in self.lexer.token_stream:
			print(t)

	def show_parse_tree(self):
		tree = self.tree
		tree.describe()

	@property
	def tree(self):
		if hasattr(self, '_tree'):
			return self._tree
		else:
			self._tree = self.parser.parse()
			return self._tree

	