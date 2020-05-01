"""
module for listing, parsing, and interpreting the built-in functions supported
by pfuncs
"""

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
			return lambda x: np.exp(self.visit(node.expr)(x))

		if (f == LOG) or (f == LN):
			return lambda x: np.log(self.visit(node.expr)(x))

		if f == LOG10:
			return lambda x: np.log10(self.visit(node.expr)(x))

		if f == SQRT:
			return lambda x: np.sqrt(self.visit(node.expr)(x))

		if f == ABS:
			return lambda x: np.abs(self.visit(node.expr)(x))

		if f == SIGN:
			return lambda x: np.sign(self.visit(node.expr)(x))

		if f == SIN:
			return lambda x: np.sin(self.visit(node.expr)(x))

		if f == COS:
			return lambda x: np.cos(self.visit(node.expr)(x))

		if f == TAN:
			return lambda x: np.tan(self.visit(node.expr)(x))

		if f == ASIN:
			return lambda x: np.arcsin(self.visit(node.expr)(x))

		if f == ACOS:
			return lambda x: np.arccos(self.visit(node.expr)(x))

		if f == ATAN:
			return lambda x: np.arctan(self.visit(node.expr)(x))

		if f == FLOOR:
			return lambda x: np.floor(self.visit(node.expr)(x))

		if f == CEIL:
			return lambda x: np.ceil(self.visit(node.expr)(x))

		if f == INT:
			return lambda x: int(self.visit(node.expr)(x))

		if f == MAX:
			raise NotImplementedError(MAX)

		if f == MIN:
			raise NotImplementedError(MIN)	

		if f == NORMCDF:
			raise NotImplementedError(NORMCDF)

		if f == NORMPDF:
			raise NotImplementedError(NORMPDF)	

		if f == ERF:
			return lambda x: erf(self.visit(node.expr)(x))