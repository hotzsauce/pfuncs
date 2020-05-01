
from pfuncs.lexer import Lexer

from pfuncs.algebra import (
	AlgebraParser,
	AlgebraInterpreter
)


class Reader(object):

	def __init__(self, text):
		self.lexer = Lexer(text)
		self.parser = AlgebraParser(self.lexer)

	def read(self):
		tree = self.tree

		self.interpreter = AlgebraInterpreter(tree)
		result = self.interpreter.interpret()

		print('{expr} = {result}'.format(
				expr=self.lexer.text,
				result=result
			)
		)

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