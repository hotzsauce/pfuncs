

from lexer import Lexer 
from algebra import (
	AlgebraParser,
	AlgebraInterpreter
)



class Tester(object):

	def __init__(self, text):
		self.lexer = Lexer(text)
		self.parser = AlgebraParser(self.lexer)

	def read(self):
		tree = self.tree

		self.interpreter = AlgebraInterpreter(tree)
		result = self.interpreter.interpret()

		return result

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



expr = '7+8*9'

T = Tester(expr)
T.summarize_tokens()
T.show_parse_tree()
print(T.read())