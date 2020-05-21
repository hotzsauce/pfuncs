
import copy

import pfuncs.ast as ast 

from pfuncs.generic import ABCVisitor
from pfuncs.tokens import Token
from pfuncs.base import NUMBER

class Curryer(ABCVisitor):
	"""
	clas that implements currying of multivariate functions. Walks over the 
	entire Abstract Syntax Tree, and every time it hits a Var node that 
	represents a variable in the scope, replaces it with a Num node withk
	the provided value
	"""

	def __init__(self, tree, scope):
		self.tree = copy.deepcopy(tree)
		self.scope = copy.deepcopy(scope)

	def curry(self):
		self.visit(self.tree)
		return self.tree

	def maybe_substitute(self, node, attr):
		attribute = getattr(node, attr)
		if isinstance(attribute, ast.Var):
			if attribute.value in self.scope.variables:
				setattr(node, attr, self.substitute(attribute))

	def substitute(self, node):
		var_name = node.value 
		var_value = self.scope.retrieve(var_name)
		token = Token(NUMBER, var_value)
		return ast.Num(token)

	def visit_BinaryOp(self, node):
		self.maybe_substitute(node, 'left')
		self.maybe_substitute(node, 'right')
		self.visit(node.left)
		self.visit(node.right)

	def visit_UnaryOp(self, node):
		self.maybe_substitute(node, 'expr')
		self.visit(node.expr)

	def visit_Num(self, node):
		pass

	def visit_Var(self, node):
		pass

	def visit_Function(self, node):
		self.maybe_substitute(node, 'expr')
		self.visit(node.expr)