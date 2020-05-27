"""
module for helpful AST-walkers & functions that use them
"""
import copy
import functools

import pfuncs.ast as ast
import pfuncs.callable as call 

from pfuncs.tokens import Token
from pfuncs.generic import ABCVisitor
from pfuncs.base import (
	NUMBER,
	PLUS,
	MINUS,
	MUL,
	DIV,
	POWER
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


class Reducer(ABCVisitor):

	# additive and multiplicative identities
	aident = 0
	mident = 1

	def __init__(self, tree):
		self.tree = self._copy(tree)

		# visit all the nodes in the usual recursive way. We call _reduce() here
		# 	in case self.tree ends up being a Binary or Unary op that can be 
		#	reduced even futher
		self.visit(self.tree)
		final_tree = self._reduce(self.tree)
		if final_tree:
			self.tree = final_tree

	def _copy(self, tree):
		return copy.deepcopy(tree)

	def _both_numbers(self, node1, node2):
		return isinstance(node1, ast.Num) and isinstance(node2, ast.Num)

	def _is_equal_to(self, node, number):
		if isinstance(node, ast.Num):
			if node.value == number:
				return True
		return False

	def _reduce_attr(self, node, attr):
		new_attr = self._reduce(getattr(node, attr))
		if new_attr:
			setattr(node, attr, new_attr)

	def _reduce(self, node):
		if isinstance(node, ast.BinaryOp):
			return self._reduce_BinaryOp(node)
		if isinstance(node, ast.UnaryOp):
			return self._reduce_UnaryOp(node)

	def _reduce_BinaryOp(self, node):
		if node.op.type == PLUS:
			return self._reduce_addition(node)
		elif node.op.type == MINUS:
			return self._reduce_subtraction(node)
		elif node.op.type == MUL:
			return self._reduce_multiplication(node)
		elif node.op.type == DIV:
			return self._reduce_division(node)
		elif node.op.type == POWER:
			return self._reduce_power(node)
		
	def _reduce_addition(self, node):
		if self._both_numbers(node.left, node.right):
			value = node.left.value + node.right.value
			return ast.Num(Token(NUMBER, value))
		elif self._is_equal_to(node.left, self.aident):
			return node.right
		elif self._is_equal_to(node.right, self.aident):
			return node.left

	def _reduce_subtraction(self, node):
		if self._both_numbers(node.left, node.right):
			value = node.left.value - node.right.value
			return ast.Num(Token(NUMBER, value))
		elif self._is_equal_to(node.left, self.aident):
			return ast.UnaryOp(
				op=Token(MINUS, '-'),
				expr=node.right
			)
		elif self._is_equal_to(node.right, self.aident):
			return node.left
		elif isinstance(node.right, ast.UnaryOp):
			if node.right.op.type == MINUS:
				setattr(node, 'op', Token(PLUS, '+'))
				setattr(node, 'right', node.expr.expr)
			return node
			
	def _reduce_multiplication(self, node):
		if self._both_numbers(node.left, node.right):
			value = node.left.value * node.right.value
			return ast.Num(Token(NUMBER, value))
		elif (
			self._is_equal_to(node.left, self.aident)
			or self._is_equal_to(node.right, self.aident)
		):
			return ast.Num(Token(NUMBER, self.aident))
		elif self._is_equal_to(node.left, self.mident):
			return node.right
		elif self._is_equal_to(node.right, self.mident):
			return node.left

	def _reduce_division(self, node):
		if self._both_numbers(node.left, node.right):
			value = node.left.value / node.right.value
			return ast.Num(Token(NUMBER, value))
		elif self._is_equal_to(node.left, self.aident):
			return ast.Num(Token(NUMBER, self.aident))
		elif self._is_equal_to(node.right, self.mident):
			return node.left

	def _reduce_power(self, node):
		if self._both_numbers(node.left, node.right):
			value = node.left.value ** node.right.value
			return ast.Num(Token(NUMBER, value))
		elif (
			self._is_equal_to(node.left, self.mident)
			or self._is_equal_to(node.left, self.aident)
		):
			return node.left
		elif self._is_equal_to(node.right, self.mident):
			return node.left
		elif self._is_equal_to(node.right, self.aident):
			return ast.Num(Token(NUMBER, self.mident))

	def _reduce_UnaryOp(self, node):
		if node.op.type == PLUS:
			return node.expr
		elif node.op.type == MINUS:
			if isinstance(node.expr, ast.UnaryOp):
				if node.expr.op.type == MINUS:
					setattr(node, 'op', Token(PLUS, '+'))
					setattr(node, 'expr', node.expr.expr)
				elif node.expr.op.type == PLUS:
					setattr(node, 'expr', node.expr.expr)
				return node

	def visit_BinaryOp(self, node):
		self.visit(node.left)
		self.visit(node.right)

		self._reduce_attr(node, 'left')
		self._reduce_attr(node, 'right')
			

	def visit_UnaryOp(self, node):
		self.visit(node.expr)
		self._reduce_attr(node, 'expr')


	def visit_Num(self, node):
		pass

	def visit_Var(self, node):
		pass

	def visit_Function(self, node):
		self.visit(node.expr)
		self._reduce_attr(node, 'expr')


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


def simplify(func):
	""" 
	decorator for class methods that return a Func instance. Uses the Reducer 
	class to algebraically simplify the AST
	"""

	@functools.wraps(func)
	def reduce(self=None, *args, **kwargs):
		obj = func(self, *args, **kwargs)
		try:
			red = Reducer(obj.tree)
			return call.Func(tree=red.tree)
		except AttributeError:
			# if func() is an fully evaluated Differential object, 'obj' will
			#	just be a number
			return call.Func(str(obj))

	return reduce


def ensure_func(f):
	if isinstance(f, call.Func):
		return f 
	elif isinstance(f, str):
		return call.Func(f)
	elif isinstance(f, (int, float)):
		return call.Func(str(f))
	else:
		raise TypeError(repr(f))