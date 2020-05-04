

from pfuncs.base import NUMBER
from pfuncs.generic import ABCVisitor


class Symbol(object):

	def __init__(self, name, stype=None):
		self.name = name
		self.stype = stype


class BuiltinTypeSymbol(Symbol):

	def __init__(self, name):
		super().__init__(name)

	def __str__(self):
		return self.name

	def __repr__(self):
		return '<{klass}({name})>'.format(
				klass=self.__class__.__name__,
				name=self.name
		)


class VarSymbol(Symbol):

	def __init__(self, name, stype):
		super().__init__(name, stype)

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		return '<{klass}({name}: {stype})>'.format(
				klass=self.__class__.__name__,
				name=self.name,
				stype=self.stype
		)


class ScopedSymbolTable(object):

	def __init__(self, scope_name, scope_level):
		self._symbols = {}
		self.scope_name = scope_name
		self.scope_level = scope_level
		self._init_builtins()

	def _init_builtins(self):
		self.insert(BuiltinTypeSymbol(NUMBER))

	def insert(self, symbol):
		self._symbols[symbol.name] = symbol

	def lookup(self, name):
		return self._symbols.get(name)

	@property
	def nonbuiltins(self):
		return [k 
				for k, v in self._symbols.items() 
				if not isinstance(v, BuiltinTypeSymbol)
		]
	

	def __str__(self):

		n_delims = 50
		h1 = 'SCOPE (Scoped Symbol Table)'
		lines = ['\n', h1, '='*n_delims]
		for header_name, header_value in (
			('Scope Name', self.scope_name),
			('Scope Level', self.scope_level)
		):
			lines.append('{:<15}: {}'.format(header_name, header_value))

		h2 = 'Scope (Scoped Symbol Table) Contents'
		lines.extend([h2, '-'*n_delims])
		lines.extend(
			(('{:>15}: {}').format(k, v)
			for k, v in self._symbols.items()
			if not isinstance(v, BuiltinTypeSymbol))
		)
		lines.append('\n')
		return '\n'.join(lines)


class SemanticAnalyzer(ABCVisitor):

	def __init__(self, tree):
		super().__init__(tree)
		self.scope = ScopedSymbolTable(
						scope_name='global',
						scope_level=1
		)

	# ALGEBRA & FUNCTIONS
	def visit_BinaryOp(self, node):
		self.visit(node.left)
		self.visit(node.right)

	def visit_UnaryOp(self, node):
		self.visit(node.expr)

	def visit_Num(self, node):
		pass

	def visit_Var(self, node):
		# for the moment we're only concerned with scalar entries
		stype = self.scope.lookup(NUMBER)

		# name of the variable, i.e. 'x' or 'y'
		var_name = node.value
		var_symbol = VarSymbol(var_name, stype)
		
		self.scope.insert(var_symbol)

	def visit_Function(self, node):
		pass

	def analyze(self):
		self.visit(self.tree)

	@property
	def variables(self):
		return tuple(self.scope.nonbuiltins)
	

	def __repr__(self):
		return '<{class_name} Object>'.format(
				class_name=self.__class__.__name__
		)

	def __str__(self):
		header = '\n{class_name} with Underlying Table:'.format(
					class_name=self.__class__.__name__
		)
		return ''.join([header, self.scope.__str__()])