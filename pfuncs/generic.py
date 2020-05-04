"""
module with Abstract Base Classes for parsers, and AST-climbing objects
"""

class ABCParser(object):
	""" Abstract Base Class for parser """

	def __init__(self, lexer):
		self.lexer = lexer
		self.current_token = self.lexer.get_next_token()

	def error(self):
		raise Exception(self.current_token)

	def eat(self, token_type):
		"""
		compare the current token type with the passed token type and if they
		match, eat the current token and assign the next token to the 
		self.current_token. Otherwise, throw and error
		"""
		if self.current_token.type == token_type:
			self.current_token = self.lexer.get_next_token()
		else:
			self.error()

	def peek(self):
		return self.lexer.get_next_token()


class ABCVisitor(object):
	""" Abstract Base Class for AST node visitors """
	def __init__(self, tree):
		self.tree = tree

	def visit(self, node):
		method = 'visit_' + type(node).__name__
		visitor = getattr(self, method, self._nonexistent_node)
		return visitor(node)

	def _nonexistent_node(self, node):
		raise Exception('No visit_{} method'.format(type(node).__name__))