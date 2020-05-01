"""
module with non-function keywords & key symbols used throughout pfuncs, as 
well as a few validators used by the lexer
"""

COMMA 	= 'COMMA'
ID 		= 'ID'
NUMBER 	= 'NUMBER'
EOF 	= 'EOF'
LPARE 	= '('
RPARE 	= ')'

PLUS 	= 'PLUS'
MINUS 	= 'MINUS'
MUL 	= 'MUL'
DIV 	= 'DIV'
POWER 	= 'POWER'


def is_valid_varchar(c):
	# checks character is a valid character for a variable name: 
	# 	underscores, numbers, letters
	try:
		return c.isalnum() or c == '_'
	except AttributeError:
		return False

def is_valid_varname_firstchar(c):
	# variable names can begin with underscores or letters
	try:
		return c.isalpha() or c == '_'
	except AttributeError:
		return False

def is_valid_numchar(c):
	# numbers can begin with number or decimal
	try:
		return c.isdigit() or c == '.'
	except AttributeError:
		return False