
from pfuncs.lexer import Lexer

from pfuncs.functions import (
	FunctionParser,
	FunctionInterpreter
)


class Reader(object):

	def __init__(self, text):
		self.lexer = Lexer(text)
		self.parser = FunctionParser(self.lexer)

	def read(self):
		tree = self.tree

		self.interpreter = FunctionInterpreter(tree)
		result = self.interpreter.interpret()

		print('{expr} = {result}'.format(
				expr=self.lexer.text,
				result=result
			)
		)

	def call(self):
		tree = self.tree
		self.interpreter = FunctionInterpreter(tree)
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

	