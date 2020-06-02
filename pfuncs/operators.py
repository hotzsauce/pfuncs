""" 
module for operators that accept ASTs (and, optionally, scopes) and modifies
them in some way
"""

import copy

import pfuncs.ast as ast 
import pfuncs.callable as call
import pfuncs.functions as fnc

from pfuncs.generic import ABCVisitor
from pfuncs.tokens import Token
from pfuncs.utils import (
	is_constant,
	simplify
)
from pfuncs.base import (
	# number used in Curryer
	NUMBER,
	# mathematical operations used in _Jacobian
	PLUS,
	MINUS,
	MUL,
	DIV,
	POWER
)


class Curryer(ABCVisitor):
	"""
	class that implements currying of multivariate functions. Walks over the 
	entire Abstract Syntax Tree, and every time it hits a Var node that 
	represents a variable in the scope, replaces it with the argument
	"""

	def __init__(self, tree, scope):
		self.tree = copy.deepcopy(tree)
		self.scope = copy.deepcopy(scope)

	def curry(self):
		self.visit(self.tree)
		return call.Func(tree=self.tree)

	def maybe_substitute(self, node, attr):
		attribute = getattr(node, attr)
		if isinstance(attribute, ast.Var):
			if attribute.value in self.scope.variables:
				setattr(node, attr, self.substitute(attribute))

	def substitute(self, node):
		""" 
		four cases for substituting: Func obj, or parse-able string, 
		number or ndarray-type object 
		"""
		var_name = node.value 
		var_value = self.scope.retrieve(var_name)

		if isinstance(var_value, call.Func):
			return var_value.tree
		elif isinstance(var_value, str):
			sub_func = call.Func(var_value)
			return sub_func.tree
		else:
			token = Token(NUMBER, var_value)
			return ast.Num(token)

	def visit_BinaryOp(self, node):
		self.visit(node.left)
		self.visit(node.right)
		self.maybe_substitute(node, 'left')
		self.maybe_substitute(node, 'right')
		
	def visit_UnaryOp(self, node):
		self.visit(node.expr)
		self.maybe_substitute(node, 'expr')
		
	def visit_Num(self, node):
		pass

	def visit_Var(self, node):
		pass

	def visit_Function(self, node):
		self.maybe_substitute(node, 'expr')
		self.visit(node.expr)

	def visit_MultivarFunction(self, node):
		for arg in node.arguments:
			self.maybe_substitute(arg, 'expr')
			self.visit(arg)
			
	def visit_Arg(self, node):
		self.visit(node.expr)


class _Jacobian(ABCVisitor, fnc.FunctionDerivative):
	"""
	class the implements derivatives of functions. Walks over the entire
	Abstract Syntax Tree
	"""

	def __init__(self, tree, diff_var):
		self.tree = self._copy(tree)
		self.diff_var = diff_var

		self.visit(self.tree)

	def _is_constant(self, node):
		return is_constant(node, self.diff_var)

	def _copy(self, tree):
		return copy.deepcopy(tree)

	def maybe_singleton(self, node, attr):
		"""
		Checks if node's attr attribute if it is a singleton - a Var, Num or 
		Function node. If so, take the derivative of it. If not, walk the 
		attribute as normal
		"""
		attribute = getattr(node, attr)
		if isinstance(attribute, ast.Var):
			if attribute.value == self.diff_var:
				setattr(node, attr, ast.Num(Token(NUMBER, 1)))
			else:
				setattr(node, attr, ast.Num(Token(NUMBER, 0)))
		elif isinstance(attribute, ast.Num):
			setattr(node, attr, ast.Num(Token(NUMBER, 0)))
		elif isinstance(attribute, ast.Function):
			setattr(node, attr, self._chain_rule(attribute))
		elif isinstance(attribute, ast.MultivarFunction):
			raise NotImplementedError
		else:
			self.visit(attribute)

	def _new_binary(self, left, op, right):
		""" utility function used in the _*_rules """
		return ast.BinaryOp(left=left,
			op=op,
			right=right
		)

	def _chain_rule(self, node):
		"""
		Use function_derivative method of the FunctionDerivative superclass to 
		compute the derivative of the functions. That method doesn't use the 
		Chain Rule though; i.e. it handles f(g(x)) as if it's f(x). So, we 
		multiply by g'(x) here (if necessary)
		"""
		gprime = self._copy(node)
		self.maybe_singleton(gprime, 'expr')
		fprime = self.function_derivative(node)

		return ast.BinaryOp(
			left=gprime.expr,
			op=Token(MUL, '*'),
			right=fprime
		)

	def _product_rule(self, node):
		"""
		(f*g)' = f'*g + f*g' 
		"""

		# The pairing of left_copy with maybe_singleton's 'left' argument, and 
		# right_copy with the 'right' argument is not important for the product 
		# rule here. But, because the _quotient_rule method makes use of this
		# method, those pairings can't be switched
		left_copy = self._copy(node)
		right_copy = self._copy(node)

		# making the f'*g term
		node.op = Token(PLUS, '+')
		self.maybe_singleton(left_copy, 'left')
		node.left = self._new_binary(
			left=left_copy.left,
			op=Token(MUL, '*'),
			right=left_copy.right
		)

		# making the f*g' term
		self.maybe_singleton(right_copy, 'right')
		node.right = self._new_binary(
			left=right_copy.left,
			op=Token(MUL, '*'),
			right=right_copy.right
		)

	def _quotient_rule(self, node):
		"""
		(f/g)' = (g*f' - f*g')/(g^2)
		"""

		# use the product rule method to evaluate the numerator, then replace the
		#	plus sign with a minus
		num_copy = self._copy(node)
		self._product_rule(num_copy)
		num_copy.op = Token(MINUS, '-')

		# squaring the denominator function with _new_binary
		node.right = self._new_binary(
			left=self._copy(node.right),
			op=Token(POWER, '**'),
			right=ast.Num(Token(NUMBER, 2))
		)
		node.op = Token(DIV, '/')
		node.left = num_copy

	def _power_rule(self, node):
		"""
		This method covers more than just the basic (x^a)' = a*x^(a-1). There
		are four cases. If:
			Base & Exponent Constant 	- left and right nodes set to 0
			B Constant, E Not 			- (a^f)' = ln(a)*f'*a^f
			B Not, E Constant 			- basic power rule
			B Not, E Not 				- (f^g)' = (f^g)*((g*f')/f + g'*ln(f))

		Here's the algebra for the fourth case. Define y = f^g. Then
				ln(y) = g*ln(f)
			 [ln(y)]' = g * (f'/f) + g'*ln(f)
			 (y'/y)   = g * (f'/f) + g'*ln(f)
			  y' 	  = y * ((g*f')/f + g'*ln(f))
		"""

		base_const = self._is_constant(node.left)
		expo_const = self._is_constant(node.right)

		if base_const and expo_const:
			node.left = ast.Num(Token(NUMBER, 0))
			node.op = Token(MUL, '*')
			node.right = ast.Num(Token(NUMBER, 0))

		elif base_const and (not expo_const):
			# first copy is used to evaluate the ln(a) and f' coefficient terms;
			# 	the second copy is used to track the full remaining a^f term
			coef_copy = self._copy(node)
			full_copy = self._copy(node)

			# evaluating the f' term
			self.maybe_singleton(coef_copy, 'right')

			# the ln(a) coefficient
			node.left = ast.Function(
				token=Token(fnc.FUNCTION, fnc.LN),
				expr=coef_copy.left
			)
			node.op = Token(MUL, '*')

			node.right = self._new_binary(
				left=coef_copy.right,
				op=Token(MUL, '*'),
				right=full_copy
			)

		elif (not base_const) and expo_const:
			node_copy = self._copy(node)

			node.left = node_copy.right
			node.op = Token(MUL, '*')
			node.right = self._new_binary(
				left=node_copy.left,
				op=Token(POWER, '**'),
				right=self._new_binary(
					left=node_copy.right,
					op=Token(MINUS, '-'),
					right=ast.Num(Token(NUMBER, 1))
				)
			)

		elif (not base_const) and (not expo_const):

			node_copy = self._copy(node)
			prime_copy = self._copy(node)

			self.maybe_singleton(prime_copy, 'left')
			self.maybe_singleton(prime_copy, 'right')

			f, g = node_copy.left, node_copy.right
			fp, gp = prime_copy.left, node_copy.right

			lnf = ast.Function(
				token=Token(fnc.FUNCTION, fnc.LN),
				expr=self._copy(f)
			)

			gfp = ast.BinaryOp(
				left=g, op=Token(MUL, '*'), right=fp
			)
			gfpf = ast.BinaryOp(
				left=gfp, op=Token(DIV, '/'), right=f
			)
			gplnf = ast.BinaryOp(
				left=gp, op=Token(MUL, '*'), right=lnf
			)

			node.left = node_copy
			node.op = Token(MUL, '*')
			node.right = ast.BinaryOp(
				left=gfpf, op=Token(PLUS, '+'), right=gplnf
			)

	def visit_BinaryOp(self, node):
		"""
		for products, divisions, and exponents, use their respective methods. For
		addition and subtraction, check to see if the 'left' and 'right' nodes
		are singleton variables before visiting their children ASTs
		"""
		if node.op.type == PLUS:
			self.maybe_singleton(node, 'left')
			self.maybe_singleton(node, 'right')
		elif node.op.type == MINUS:
			self.maybe_singleton(node, 'left')
			self.maybe_singleton(node, 'right')
		elif node.op.type == MUL:
			self._product_rule(node)
		elif node.op.type == DIV:
			self._quotient_rule(node)
		elif node.op.type == POWER:
			self._power_rule(node)

	def visit_UnaryOp(self, node):
		""" Check if singleton variable; visit child nodes if not """
		self.maybe_singleton(node, 'expr')

	def visit_Num(self, node):
		""" 
		if this node is reached it means the entire tree is just the one 
		number node. In larger trees, the maybe_singleton method handles
		numbers within binary & unary operations, and expressions
		"""
		self.tree = ast.Num(Token(NUMBER, 0))
		
	def visit_Var(self, node):
		""" 
		if this node is reached it means the entire tree is just the one 
		variable node. In larger trees, the maybe_singleton method handles
		variables within binary & unary operations, and expressions
		"""
		if node.value == self.diff_var:
			self.tree = ast.Num(Token(NUMBER ,1))
		else:
			self.tree = ast.Num(Token(NUMBER, 0))

	def visit_Function(self, node):
		""" 
		if this node is reached it means the entire tree is just the one 
		function node. In larger trees, the maybe_singleton method handles
		functions within binary & unary operations, and expressions
		"""
		self.tree = self._chain_rule(node)

	def visit_MultivarFunction(self, node):
		""" 
		if this node is reached it means the entire tree is just the one 
		multivarvunction node. In larger trees, the maybe_singleton method handles
		multivarfunctions within binary & unary operations, and expressions
		"""
		raise NotImplementedError


class Differential(object):
	"""
	Class that's instantiated when the .d or .derivative property of a Funcs
	instance is accessed
	"""

	def __init__(self, tree):
		self.tree = tree

	@simplify
	def __getitem__(self, key):
		if isinstance(key, str):
			f_prime = _Jacobian(self.tree, key)
			return call.Func(tree=f_prime.tree)

		elif isinstance(key, tuple):
			tree = copy.deepcopy(self.tree)
			for k in reversed(key):
				dfdk = _Jacobian(tree, k)
				tree = dfdk.tree
			return call.Func(tree=tree)

		elif isinstance(key, dict):
			tree = copy.deepcopy(self.tree)
			for k in reversed(tuple(key.keys())):
				dfdk = _Jacobian(tree, k)
				tree = dfdk.tree
			f_prime = call.Func(tree=tree)
			return f_prime(**key)