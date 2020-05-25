"""
module for listing, parsing, and interpreting the built-in functions supported
by pfuncs. Both Parser and Interpreter inherit most of the their functionality
from the analogous objects in pfuncs.algebra
"""
import copy
import numpy as np
from scipy.special import erf

import pfuncs.ast as ast 
import pfuncs.base as base
import pfuncs.algebra as alg

from pfuncs.tokens import Token 


FUNCTION 	= 'FUNCTION'

EXP 	= 'exp'
LOG 	= 'log'
LN		= 'ln'
LOG10 	= 'log10'
SQRT 	= 'sqrt'
ABS 	= 'abs'
SIGN 	= 'sign'
SIN 	= 'sin'
COS 	= 'cos'
TAN 	= 'tan'
ASIN 	= 'asin'
ACOS 	= 'acos'
ATAN 	= 'atan'
FLOOR  	= 'floor'
CEIL 	= 'ceil'
INT 	= 'int'
MAX 	= 'max'
MIN 	= 'min'
NORMCDF = 'normcdf'
NORMPDF = 'normpdf'
ERF 	= 'erf'


RESERVED_KEYWORDS = {
	EXP: 		Token(FUNCTION, EXP),
	LOG: 		Token(FUNCTION, LOG),
	LN: 		Token(FUNCTION, LN),
	LOG10: 		Token(FUNCTION, LOG10),
	SQRT: 		Token(FUNCTION, SQRT),
	ABS: 		Token(FUNCTION, ABS),
	SIGN: 		Token(FUNCTION, SIGN),
	SIN: 		Token(FUNCTION, SIN),
	COS: 		Token(FUNCTION, COS),
	TAN: 		Token(FUNCTION, TAN),
	ASIN: 		Token(FUNCTION, ASIN),
	ACOS: 		Token(FUNCTION, ACOS),
	ATAN: 		Token(FUNCTION, ATAN),
	FLOOR: 		Token(FUNCTION, FLOOR),
	CEIL:		Token(FUNCTION, CEIL),
	INT: 		Token(FUNCTION, INT),
	MAX: 		Token(FUNCTION, MAX),
	MIN: 		Token(FUNCTION, MIN),
	NORMCDF: 	Token(FUNCTION, NORMCDF),
	NORMPDF: 	Token(FUNCTION, NORMPDF),
	ERF: 		Token(FUNCTION, ERF)
}


class Parser(alg.Parser):
	""" 
	The pfuncs.functions.Parser adds a call() method between the exponent() and 
	atom() methods of the super-class pfuncs.algebra.Parser
	"""

	def __init__(self, lexer):
		super().__init__(lexer)

	def call(self):
		node = self.atom()

		while self.current_token.type == FUNCTION:
			token = self.current_token
			self.eat(FUNCTION)
			self.eat(base.LPARE)

			node = ast.Function(token=token,
								expr=self.expr())
			self.eat(base.RPARE)

		return node

	def exponent(self):
		node = self.call()

		while self.current_token.type == base.POWER:
			token = self.current_token
			self.eat(base.POWER)

			node = ast.BinaryOp(left=node,
								op=token,
								right=self.exponent())
		return node


class Interpreter(alg.Interpreter):
	"""
	Augments pfuncs.algebra.Interpreter by adding visit_Function method
	"""

	def visit_Function(self, node):
		f = node.value

		if f == EXP:
			return np.exp(self.visit(node.expr))
	
		if (f == LOG) or (f == LN):
			return np.log(self.visit(node.expr))

		if f == LOG10:
			return np.log10(self.visit(node.expr))

		if f == SQRT:
			return np.sqrt(self.visit(node.expr))

		if f == ABS:
			return np.abs(self.visit(node.expr))

		if f == SIGN:
			return np.sign(self.visit(node.expr))

		if f == SIN:
			return np.sin(self.visit(node.expr))

		if f == COS:
			return np.cos(self.visit(node.expr))

		if f == TAN:
			return np.tan(self.visit(node.expr))

		if f == ASIN:
			return np.arcsin(self.visit(node.expr))

		if f == ACOS:
			return np.arccos(self.visit(node.expr))

		if f == ATAN:
			return np.arctan(self.visit(node.expr))

		if f == FLOOR:
			return np.floor(self.visit(node.expr))

		if f == CEIL:
			return np.ceil(self.visit(node.expr))

		if f == INT:
			return int(self.visit(node.expr))

		if f == MAX:
			raise NotImplementedError(MAX)

		if f == MIN:
			raise NotImplementedError(MIN)	

		if f == NORMCDF:
			raise NotImplementedError(NORMCDF)

		if f == NORMPDF:
			raise NotImplementedError(NORMPDF)	

		if f == ERF:
			return erf(self.visit(node.expr))


class FunctionDerivative(object):

	def _copy(self, tree):
		return copy.deepcopy(tree)

	def function_derivative(self, node):
		method = 'diff_' + node.value
		fprime = getattr(self, method, self._notimplemented_diff)
		return fprime(node)

	def _notimplemented_diff(self, node):
		msg = 'Derivative for {} not implemented.'
		raise NotImplementedError(msg.format(repr(node.value)))

	def diff_exp(self, node):
		""" e^x -> e^x """
		return self._copy(node)

	def diff_log(self, node):
		""" log(x) -> x^(-1) """
		return ast.BinaryOp(
			left=self._copy(node.expr),
			op=Token(base.POWER, '**'),
			right=ast.Num(Token(base.NUMBER, -1))
		)

	def diff_ln(self, node):
		""" log(x) -> x^(-1) """
		return self.diff_log(node)

	def diff_log10(self, node):
		""" log10(x) -> (x*ln(10))^(-1) """
		denom = ast.BinaryOp(
			left=self._copy(node.expr),
			op=Token(base.MUL, '*'),
			right=ast.Num(Token(base.NUMBER, np.log(10)))
		)
		return ast.BinaryOp(
			left=denom,
			op=Token(base.POWER, '**'),
			right=ast.Num(Token(base.NUMBER, -1))
		)

	def diff_sqrt(self, node):
		""" sqrt(x) -> (2*x^(1/2))^(-1) """
		radical = ast.BinaryOp(
			left=self._copy(node.expr),
			op=Token(base.POWER, '**'),
			right=ast.Num(Token(base.NUMBER, -1/2))
		)
		return ast.BinaryOp(
			left=radical,
			op=Token(base.DIV, '/'),
			right=ast.Num(Token(base.NUMBER, 2))
		)

	def diff_sin(self, node):
		""" cos(x) -> sin(x) """
		return ast.Function(
			token=Token(FUNCTION, COS),
			expr=self._copy(node.expr)
		)

	def diff_cos(self, node):
		""" cos(x) -> -sin(x) """
		sine = ast.Function(
			token=Token(FUNCTION, SIN),
			expr=self._copy(node.expr)
		)
		return ast.UnaryOp(
			op=Token(base.MINUS, '-'),
			expr=sine
		)

	def diff_tan(self, node):
		""" tan(x) -> (cos(x))^(-2) """
		cosine = ast.Function(
			token=Token(FUNCTION, COS),
			expr=self._copy(node.expr)
		)
		return ast.BinaryOp(
			left=cosine,
			op=Token(base.POWER, '**'),
			right=ast.Num(Token(base.NUMBER, -2))
		)

	def diff_asin(self, node):
		""" asin(x) -> (1 - x^2)^(-1/2) """
		xsq = ast.BinaryOp(
			left=self._copy(node.expr),
			op=Token(base.POWER, '**'),
			right=ast.Num(Token(base.NUMBER, 2))
		)
		one_minus_xsq = ast.BinaryOp(
			left=ast.Num(Token(base.NUMBER, 1)),
			op=Token(base.MINUS, '-'),
			right=xsq
		)
		return ast.BinaryOp(
			left=one_minus_xsq,
			op=Token(base.POWER, '**'),
			right=ast.Num(Token(base.NUMBER, -1/2))
		)

	def diff_acos(self, node):
		""" acos(x) -> -(1 - x^2)^(-1/2) """
		radical = self.diff_asin(node)
		return ast.UnaryOp(
			op=Token(base.MINUS, '-'),
			expr=radical
		)

	def diff_atan(self, node):
		""" atan(x) -> (1 + x^2)^(-1) """
		xsq = ast.BinaryOp(
			left=self._copy(node.expr),
			op=Token(base.POWER, '**'),
			right=ast.Num(Token(base.NUMBER, 2))
		)
		one_plus_xsq = ast.BinaryOp(
			left=ast.Num(Token(base.NUMBER, 1)),
			op=Token(base.PLUS, '+'),
			right=xsq
		)
		return ast.BinaryOp(
			left=one_plus_xsq,
			op=Token(base.POWER, '**'),
			right=ast.Num(Token(base.NUMBER, -1))
		)