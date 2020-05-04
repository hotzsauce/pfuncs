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