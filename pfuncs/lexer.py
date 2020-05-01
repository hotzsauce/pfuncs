

import pfuncs.base as base
import pfuncs.functions as fnc 

from pfuncs.tokens import Token 

RESERVED_KEYWORDS = {
	**fnc.RESERVED_KEYWORDS
}

class Lexer(object):

	def __init__(self, text):
		self.text = text

		self.pos = self.token_pos = 0
		self.current_char = self.text[self.pos]
		self.token_stream = list()

		self.tokenize()

	def error(self, char):
		msg = 'Invalid character: {}'.format(repr(char))
		raise Exception(msg)

	def advance(self):
		""" advance the char position and set the new current char """
		self.pos += 1
		try:
			self.current_char = self.text[self.pos]
		except IndexError:
			self.current_char = None

	def peek(self):
		""" looks at the character after the current char """
		peek_pos = self.pos + 1
		try:
			return self.text[peek_pos]
		except IndexError:
			return None

	def skip_whitespace(self):
		while (
			self.current_char is not None 
			and self.current_char.isspace()
		):
			self.advance()

	def _id(self):
		result = ''
		while base.is_valid_varchar(self.current_char):
			result += self.current_char
			self.advance()
		token = RESERVED_KEYWORDS.get(result, Token(base.ID, result))
		return token

	def number(self):
		result = ''
		while (
			self.current_char is not None 
			and base.is_valid_numchar(self.current_char)
		):
			result += self.current_char
			self.advance()
		try:
			token = Token(base.NUMBER, float(result))
		except ValueError:
			# in case there's more than one decimal, basically
			raise ValueError(result) from None
		return token

	def next_token(self):

		while self.current_char is not None:

			if self.current_char.isspace():
				self.skip_whitespace()

			if base.is_valid_varname_firstchar(self.current_char):
				return self._id()

			if base.is_valid_numchar(self.current_char):
				return self.number()

			if (
				self.current_char == '*'
				and self.peek() == '*'
			):
				self.advance()
				self.advance()
				return Token(base.POWER, '**')

			if self.current_char == '*':
				self.advance()
				return Token(base.MUL, '*')

			if self.current_char == '/':
				self.advance()
				return Token(base.DIV, '/')

			if self.current_char == '+':
				self.advance()
				return Token(base.PLUS, '+')

			if self.current_char == '-':
				self.advance()
				return Token(base.MINUS, '-')

			if self.current_char == '(':
				self.advance()
				return Token(base.LPARE, '(')

			if self.current_char == ')':
				self.advance()
				return Token(base.RPARE, ')')

			if self.current_char is not None:
				self.error(self.current_char)
			


	def tokenize(self):
		""" reads the source codes and generates a list of tokens from it """
		while self.current_char is not None:
			t = self.next_token()
			# 'if' only necessary b/c self.next_token() returns None when Lexer 
			#	reaches the end of the source code. Probably indicates this 
			#	part needs to be refactored sometime
			if isinstance(t, Token):
				self.token_stream.append(t)
		self.token_stream.append(Token(base.EOF, None))


	def get_next_token(self):
		"""
		Returns the token at the current token position (it's the next token from
		the Parser's perspective, however, hence the name), and iterates the token
		position by one
		"""
		token = self.token_stream[self.token_pos]
		self.token_pos += 1 
		return token


