# pfuncs #


### Description ###

A simple library that translates strings of mathematical expressions into
callable functions. Several common built-in functions are implemented.


### The call( ) Method ###
All parsing & interpreting is handled by the top-level `call` method. It accepts
a mathematical expression (as a string) and returns a callable that evaluates the
given expression


### Examples ###
1. Using the fixed point of $f(x) = 1 + 1/x$ to approximate the Golden Ratio
```python
phi = pfuncs.call('1/x + 1')
p = 1
for _ in range(30):
		p = phi(p)
print(p) 	# 1.6180339887496482
```

2. We can approximate Euler's constant $e$ using the first (historical) formula
```python
euler = pfuncs.call('(1 + 1/n)**n')
print(euler(100))		# 2.704814
print(euler(5000)) 	# 2.718010
```
The convergence of this formula is obviously very slow, so `pfuncs` recognizes 'e' as a special constants in expressions:
```python
print(pfuncs.call('e')) 	# 2.718281828459045
```

3. Expressions with an arbitrary number of variables can also be translated to a function, provided the values are provided as keyword arguments when the function is called. Here we calculate the total payment on a 30-year mortgage, compounded monthly:
```python
mortgage = pfuncs.call('p*(1 + r/12)**(12 * 30)')
principal, rate = 180000, 2/100
print(mortgage(p=principal, r=rate)) 	# 327817.616263
principal, rate = 195000, 4/100
print(mortgage(p=principal, r=rate)) 	# 646132.112848
```


### Built-in Functions ###
The following functions are recognized as built-in functions by `pfuncs`:
* e^x, $exp()$
* natural log, $log()$ or $ln()$
* log base 10, $log10()$
* square root, $sqrt()$
* absolute value, $abs()$
* signum function, $sign()$
* sine, $sin()$
* cosine, $cos()$
* tangent, $tan()$
* arcsine, $arcsin()$
* arccosine, $arccos()$
* floor function, $floor()$
* ceiling function, $ceil()$
* integer function, $int()$
* Gaussian error function, $erf()$

Additionally, the following are recognized, but not implemented. I didn't really feel like parsing commas & optional parameters yet:
* minimum, $min(a, b, c, ...)$
* maximum, $max(a, b, c, ...)$
* normal cumulative distribution function, $normcdf(x, mu, sigma)$
* normal probability distribution function, $normcdf(x, mu, sigma)$


### Notes ###
* expressions are case-sensitive, so all built-in functions and constants ($e$ and $pi$ for now) need to be lowercase
* although not explicitly designed to handle numpy ndarray inputs, pfuncs accepts and evaluates them correctly as variable inputs. However, the Lexer and Parser are not designed to handle them as a term in the string expression


### Thanks ###
The parsing & interpreting framework are based almost solely on [Ruslan Spivak's wonderful _Let's Build a Simple Interpreter_](https://ruslanspivak.com/lsbasi-part1/) series of blog posts


### To-Do ###
* Implement the minumum, maximum, CDF, and PDF functions
* Allow for complex numbers. Went to all that trouble to implement $e$ - might as well make use of it.
* (?) If a value is not provided for a multi-variate function, return another function that will accept that variable as an argument; i.e. allow for currying
* (?) If a lexeme is tagged as an ID, search local namespace for that string & assume it's a function, thereby allowing for composition of functions