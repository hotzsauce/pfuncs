"""
module defining the Func class - the central class of the pfuncs library
"""

import pfuncs.ast as ast
import pfuncs.base as base
import pfuncs.utils as utils

from pfuncs.tokens import Token
from pfuncs.lexer import Lexer 
from pfuncs.semantics import (
	SemanticAnalyzer,
 	ScopedMemory
)
from pfuncs.functions import (
	Parser,
	Interpreter
)
from pfuncs.operators import (
	Curryer,
	Differential
)


class Func(object):
	"""
	Func class
	=============================================================================
	initialized two different ways:
		1) with string of a mathematical expression (text parameter)
		2) with an Abstract Syntax Tree (tree parameter)

	attributes
		tree 		- Abstract Syntax Tree representing the underlying expression 
						of Func
		variables 	- tuple of strings of the variables in underlying expression
		scope 		- ScopedMemory object (dict-like) that holds the values of 
						arguments each time an instance of Func is called
		text 		- only assigned if instance is initialized with 'text'
						parameter (for now)
	"""

	def __init__(
		self, 
		text=None, 
		tree=None
	):
		self.scope = None

		if text and (tree is None):
			self._text_construct(text)
		elif (text is None) and tree:
			self._tree_construct(tree)
		else:
			msg = 'Exactly one of \'text\' and \'tree\' must be provided'
			raise ValueError(msg)


	# ============================== 
	# 	Initialization Methods 
	# ==============================
	def _text_construct(self, text):
		""" constructor method if 'text' parameter is passed to __init__ """
		lexer = Lexer(text)
		parser = Parser(lexer)
		self.tree = parser.parse()
		self._init_variables()

	def _tree_construct(self, tree):
		""" constructor method if 'tree' parameter is passed to __init__ """
		self.tree = tree
		self._init_variables()

	def _init_variables(self):
		""" search the AST for Var nodes, assign the variables attribute """
		sem_analyzer = SemanticAnalyzer(self.tree)
		sem_analyzer.analyze()
		self.variables = sem_analyzer.variables

	

	# ==============================
	# 	Calling Methods
	# ==============================
	def _call_univariate(self, *args, **kwargs):
		""" if self.variables is 1-element tuple, init scope and evaluate """
		if (len(args)==1) and (len(kwargs)==0):
			self._init_scope(arguments=args)
			return self._evaluate()
		elif (len(args)==0) and (len(kwargs)==1):
			self._init_scope(arguments=kwargs)
			return self._evaluate()
		else:
			nargs = len(args) + len(kwargs)
			msg = 'Expected one arguments; received {}'
			raise ValueError(msg.format(nargs))

	def _call_multivariate(self, *args, **kwargs):
		""" 
		if self.variables has more than one element. Must have kwargs provided. 
		If there are fewer kwargs than self.variables, curry the underlying 
		expression and return a new Func instance. If kwargs and variables are 
		of equal length, evaluate 
		"""
		if args:
			msg = 'Ambiguous arguments. For multivariate functions, use keywords'
			raise ValueError(msg)
		elif len(kwargs) < len(self.variables):
			self._init_scope(arguments=kwargs)
			return self._curry()
		elif len(kwargs) == len(self.variables):
			self._init_scope(arguments=kwargs)
			return self._evaluate()
		else:
			msg = 'Expected one arguments; received {}'
			raise ValueError(msg.format(len(kwargs)))

	def _init_scope(self, arguments):
		""" 
		given 'arguments' object from one of the _call_* methods, initialize the 
		'scope' parameter, and assign given values to the scope
		"""
		self.scope = ScopedMemory(
			scope_name='global', 
			scope_level=1
		)
		self._assign_scope(arguments)

	def _assign_scope(self, arguments):
		""" 
		assign given values to the scope. 'arguments' is dict if instance is 
		multivariate, or univariate and called with kwargs, and tuple otherwise.
		If dict keys aren't in self.variables, NameError is thrown
		"""
		if isinstance(arguments, dict):
			for k, v in arguments.items():
				if k not in self.variables:
					raise NameError(k) from None
				self.scope.assign(k, v)
		elif isinstance(arguments, tuple):
			self.scope.assign(self.variables[0], arguments[0])
		else:
			raise TypeError('arguments must be dict or tuple')

	def _evaluate(self):
		""" evaluates the expression given values of variables in self.scope """
		interpreter = Interpreter(self.tree, self.scope)
		return interpreter.interpret()

	@utils.simplify
	def _curry(self):
		return Curryer(
			tree=self.tree,
			scope=self.scope
		).curry()



	# ==============================
	# 	Calculus Methods
	# ==============================
	@property
	def derivative(self):
		""" 
		Differential class computes AST that represents the derivative, and
		can be accessed with '[]' to compute functional derivatives, and the 
		derivative at single points
		"""
		return Differential(self.tree)

	@property
	def d(self):
		""" alias for derivative property """
		return self.derivative
	
	@property
	def text(self):
		author = utils.Writer(self.tree)
		return author.write()



	# ==============================
	# 	Algebraic Methods
	# ==============================
	@utils.simplify
	def __add__(self, other):
		f = utils.ensure_func(self)
		g = utils.ensure_func(other)
		return Func(tree=utils.add(f.tree, g.tree))

	@utils.simplify
	def __radd__(self, other):
		f = utils.ensure_func(other)
		g = utils.ensure_func(self)
		return Func(tree=utils.add(f.tree, g.tree))

	@utils.simplify
	def __sub__(self, other):
		f = utils.ensure_func(self)
		g = utils.ensure_func(other)
		return Func(tree=utils.minus(f.tree, g.tree))

	@utils.simplify
	def __rsub__(self, other):
		f = utils.ensure_func(other)
		g = utils.ensure_func(self)
		return Func(tree=utils.minus(f.tree, g.tree))

	@utils.simplify
	def __mul__(self, other):
		f = utils.ensure_func(self)
		g = utils.ensure_func(other)
		return Func(tree=utils.mul(f.tree, g.tree))

	@utils.simplify
	def __rmul__(self, other):
		f = utils.ensure_func(other)
		g = utils.ensure_func(self)
		return Func(tree=utils.mul(f.tree, g.tree))

	@utils.simplify
	def __truediv__(self, other):
		f = utils.ensure_func(self)
		g = utils.ensure_func(other)
		return Func(tree=utils.div(f.tree, g.tree))

	@utils.simplify
	def __rtruediv__(self, other):
		f = utils.ensure_func(other)
		g = utils.ensure_func(self)
		return Func(tree=utils.div(f.tree, g.tree))

	@utils.simplify
	def __pow__(self, other):
		f = utils.ensure_func(self)
		g = utils.ensure_func(other)
		return Func(tree=utils.power(f.tree, g.tree))

	@utils.simplify
	def __rpow__(self, other):
		f = utils.ensure_func(other)
		g = utils.ensure_func(self)
		return Func(tree=utils.power(f.tree, g.tree))

	@utils.simplify
	def __pos__(self):
		return Func(self.text)

	@utils.simplify
	def __neg__(self):
		return Func('-' + self.text)

	def __str__(self):
		return '<{klass}: {txt}, vars: {vars}>'.format(
			klass=self.__class__.__name__,
			txt=self.text,
			vars=self.variables
		)

	def __repr__(self):
		self.tree.describe()
		return ''

	def __call__(self, *args, **kwargs):
		if len(self.variables) == 1:
			return self._call_univariate(*args, **kwargs)
		elif len(self.variables) > 1:
			return self._call_multivariate(*args, **kwargs)
		elif len(self.variables) == 0:
			return self._evaluate()