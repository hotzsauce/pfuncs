"""
module for listing, parsing, and interpreting the built-in functions supported
by pfuncs. Both Parser and Interpreter inherit most of the their functionality
from the analogous objects in pfuncs.algebra
"""
import copy
import numpy as np
import scipy.stats as stats
from scipy.special import erf

import pfuncs.ast as ast 
import pfuncs.base as base
import pfuncs.utils as utils
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
	MAX: 		Token(FUNCTION, MAX),
	MIN: 		Token(FUNCTION, MIN),
	NORMCDF: 	Token(FUNCTION, NORMCDF),
	NORMPDF: 	Token(FUNCTION, NORMPDF),
	ERF: 		Token(FUNCTION, ERF)
}

# dictioanry of function_name: max number of args
#	-1 means there is no limit
MULTIVAR_FUNCTIONS = {
	MAX: -1,
	MIN: -1, 
	NORMCDF: 3,
	NORMPDF: 3
}


class Parser(alg.Parser):
	""" 
	The pfuncs.functions.Parser adds a call() method between the exponent() and 
	atom() methods of the super-class pfuncs.algebra.Parser
	"""

	def __init__(self, lexer):
		super().__init__(lexer)

	def multivar_call(self):
		token = self.current_token
		self.eat(FUNCTION)
		self.eat(base.LPARE)

		# first argument is required
		args = [ast.Arg(self.expr())]
		
		max_arg = MULTIVAR_FUNCTIONS[token.value]
		arg_idx = 1
		while self.current_token.type == base.COMMA:
			arg_idx += 1
			if (max_arg > 0) and (arg_idx > max_arg):
				msg = '{fname} only accepts {n} arguments.'
				raise SyntaxError(msg.format(
						fname=repr(token.value),
						n=max_arg
					)
				)
			self.eat(base.COMMA)
			args.append(ast.Arg(self.expr()))

		self.eat(base.RPARE)
		
		return ast.MultivarFunction(
			token=token,
			arguments=args
		)
		
	def univar_call(self):
		token = self.current_token
		self.eat(FUNCTION)
		self.eat(base.LPARE)

		node = ast.Function(
			token=token,
			expr=self.expr()
		)
		self.eat(base.RPARE)

		return node

	def call(self):
		node = self.atom()

		while self.current_token.type == FUNCTION:
			if self.current_token.value in MULTIVAR_FUNCTIONS:
				node = self.multivar_call()
			else:
				node = self.univar_call()

		return node

	def exponent(self):
		node = self.call()

		while self.current_token.type == base.POWER:
			token = self.current_token
			self.eat(base.POWER)

			node = ast.BinaryOp(
				left=node,
				op=token,
				right=self.exponent()
			)
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

		if f == ERF:
			return erf(self.visit(node.expr))


	def visit_MultivarFunction(self, node):
		f = node.value
		args = node.arguments

		if f == MAX:
			return np.amax([self.visit(arg) for arg in args])

		if f == MIN:
			return np.amin([self.visit(arg) for arg in args])

		if f == NORMCDF:
			return stats.norm.cdf(
				self.visit(args[0]),
				self.visit(args[1]),
				self.visit(args[2])
			)

		if f == NORMPDF:
			return stats.norm.pdf(
				self.visit(args[0]),
				self.visit(args[1]),
				self.visit(args[2])
			)

	def visit_Arg(self, node):
		return self.visit(node.expr)


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
		return utils.power(
			left=self._copy(node.expr),
			right=utils.number(-1)
		)

	def diff_ln(self, node):
		""" log(x) -> x^(-1) """
		return self.diff_log(node)

	def diff_log10(self, node):
		""" log10(x) -> (x*ln(10))^(-1) """
		denom = utils.mul(
			left=self._copy(node.expr),
			right=utils.number(np.log(10))
		)
		return utils.power(
			left=denom,
			right=utils.number(-1)
		)

	def diff_sqrt(self, node):
		""" sqrt(x) -> (2*x^(1/2))^(-1) """
		radical = utils.power(
			left=self._copy(node.expr),
			right=utils.number(-1/2)
		)
		return utils.div(
			left=radical,
			right=utils.number(2)
		)

	def diff_abs(self, node):
		""" abs(x) -> sign(x) """
		return ast.Function(
			token=Token(FUNCTION, SIGN),
			expr=self._copy(node.expr)
		)

	def diff_sign(self, node):
		""" sign(x) -> 0 , ignoring undefined value at 0 """
		return utils.number(0)

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
		return utils.power(
			left=cosine,
			right=utils.number(-2)
		)

	def diff_asin(self, node):
		""" asin(x) -> (1 - x^2)^(-1/2) """
		xsq = utils.power(
			left=self._copy(node.expr),
			right=utils.number(2)
		)
		one_minus_xsq = utils.minus(
			left=utils.number(1),
			right=xsq
		)
		return utils.power(
			left=one_minus_xsq,
			right=utils.number(-1/2)
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
		xsq = utils.power(
			left=self._copy(node.expr),
			right=utils.number(2)
		)
		one_plus_xsq = utils.add(
			left=utils.number(1),
			right=xsq
		)
		return utils.power(
			left=one_plus_xsq,
			right=utils.number(-1)
		)

	def diff_floor(self, node):
		""" floor(x) -> 0, ignoring discontinuities where x is integer """
		return utils.number(0)

	def diff_ceil(self, node):
		""" ceil(x) -> 0, ignoring discontinuities where x is integer """
		return utils.number(0)

	def diff_erf(self, node):
		""" erf(x) -> (2/sqrt(pi))*exp(-x^2) """
		sqrtpi = ast.Function(
			token=Token(FUNCTION, SQRT),
			expr=ast.Num(Token(base.NUMBER, np.pi))
		)
		twopi = utils.div(
			left=utils.number(2),
			right=sqrtpi
		)

		xsq = utils.power(
			left=self._copy(node.expr),
			right=utils.number(2)
		)
		nxsq = ast.UnaryOp(
			op=Token(base.MINUS, '-'),
			expr=xsq
		)
		exp = ast.Function(
			token=Token(FUNCTION, EXP),
			expr=nxsq
		)
		return utils.mul(
			left=twopi,
			right=exp
		)