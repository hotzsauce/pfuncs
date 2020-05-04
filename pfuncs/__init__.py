
from pfuncs.lexer import Lexer

from pfuncs.functions import (
	Parser,
	Interpreter
)

from pfuncs.semantics import SemanticAnalyzer


def call(text):
	lexer = Lexer(text)
	parser = Parser(lexer)

	tree = parser.parse()

	sem_analyzer = SemanticAnalyzer(tree)
	sem_analyzer.analyze()

	interpreter = Interpreter(
					tree=tree,
					variables=sem_analyzer.variables
	)

	return interpreter.interpret()

class Caller(object):

	def __init__(self, text):
		self.lexer = Lexer(text)
		self.parser = Parser(self.lexer)

	def call(self):
		tree = self.tree

		self.sem_analyzer = SemanticAnalyzer(tree)
		self.sem_analyzer.analyze()
		var_tup = self.sem_analyzer.variables

		self.interpreter = Interpreter(
							tree=tree,
							variables=var_tup
		)
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

	