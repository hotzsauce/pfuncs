"""
module containing pfuncs-recognized constants
"""

import numpy as np 

import pfuncs.base as base 

from pfuncs.tokens import Token

E 	= 'e'
PI 	= 'pi'

RESERVED_KEYWORDS = {
	E: 	Token(base.NUMBER, np.e),
	PI: Token(base.NUMBER, np.pi)
}