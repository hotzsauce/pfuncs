"""
module for helpful AST-walkers & functions that use them
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
		super().__init__(tree)
		# self.tree = copy.deepcopy(tree)

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


class NodeFinder(ABCVisitor):
	"""
	boolean AST walker that checks if a node type is present in a tree. To be
	specific, for each node class it checks the:
		BinaryOp Node 	- operation
		UnaryOp Node 	- operation
		Num Node 		- value
		Var Node 		- variable name
		Function Node 	- function name
	"""

	def __init__(self, tree):
		super().__init__(tree)
		self.value = None
		self.has_type = False

	def contains(self, value):
		self.has_type = False
		self.value = value
		self.visit(self.tree)
		return self.has_type

	def check_match(self, node_value):
		if node_value == self.value:
			self.has_type = True

	def visit_BinaryOp(self, node):
		self.check_match(node.op.value)
		self.visit(node.left)
		self.visit(node.right)

	def visit_UnaryOp(self, node):
		self.check_match(node.op.value)
		self.visit(node.expr)

	def visit_Num(self, node):
		self.check_match(node.value)

	def visit_Var(self, node):
		self.check_match(node.value)

	def visit_Function(self, node):
		self.check_match(node.value)
		self.visit(node.expr)


def is_constant(tree, wrt):
	"""
	checks that an (full or partial) AST is constant with respect to some variable 
	"""
	checker = NodeFinder(tree)
	return not checker.contains(wrt)