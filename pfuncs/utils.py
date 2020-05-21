"""
module for helpful AST-walkers
"""
import copy

from pfuncs.generic import ABCVisitor
from pfuncs.base import (
	PLUS,
	MINUS,
	MUL,
	DIV
)


class Writer(ABCVisitor):
	"""
	AST walker that translates the tree into a human-readable string expression.
	The implementation is a little crude and results in a parentheses-laden 
	string, but the resulting string can be re-parsed to the same AST.
	"""

	def __init__(self, tree):
		self.tree = copy.deepcopy(tree)

	def add(self, new_string):
		""" so you don't see 'self.text + self.text + x' all over """
		self.text = self.text + new_string

	def visit_BinaryOp(self, node):
		self.add('(')
		self.visit(node.left)
		self.add(node.op.value)
		self.visit(node.right)
		self.add(')')

	def visit_UnaryOp(self, node):
		self.add('(')
		self.add(node.op.value)
		self.visit(node.expr)
		self.add(')')


	def visit_Num(self, node):
		""" before adding number string, check if it's a float """
		num = node.value
		num_str = str(int(num)) if int(num) == num else str(num)
		self.add(num_str)

	def visit_Var(self, node):
		var_name = node.value
		self.add(var_name)

	def visit_Function(self, node):
		self.add(node.value)
		self.add('(')
		self.visit(node.expr)
		self.add(')')

	def write(self):
		self.text = ''
		self.visit(self.tree)
		return self.text