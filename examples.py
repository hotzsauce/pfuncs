
import pfuncs as pf

# the fixed point of f(x) = 1 + 1/x to approximate the Golden Ratio
phi = pf.call('1 + 1/x')
p = 1
for _ in range(30):
	p = phi(p)
print('The Golden Ratio is approximately: {phi}\n'.format(phi=p))


# approximating Euler's constant e using the (historical) first formula for it:
euler = pf.call('(1 + 1/n)**n')
for n in [10, 50, 100, 500, 1000, 5000]:
	print('After {n:>5} iterations, Euler\'s Constant is approximately {e:f}'.format(
			n=n,
			e=euler(n))
	)
print(' ')


# pfuncs does recognize 'e' as a special constant though:
e_constant = pf.call('e')
for i in range(0, 2):
	print('Euler\'s Constant: {}'.format(e_constant()))
print(' ')


# pfuncs can parse functions with an arbitrary number of variables, but when it
#	is called, kwargs must be used to avoid ambiguity.
# As an example, we can calculate the final amount paid on a thirty year mortgage 
# 	compounded monthly on a house that costs principal $p, with interest rate r
mtg = pf.call('p*(1 + r/12)**(12*30)')
for rate in range(2, 5):
	for principal in range(150000, 210000, 15000):
		amt = mtg(p=principal, r=rate/100)
		print('You would pay {amt:f} total on a {p} house with rate {ir}%'.format(
				amt=amt,
				p=principal,
				ir=rate)
		)
	print(' ')


# another multivariable example: length of the shadow of a building h feet high
#	tilting at theta degrees (pi is a recognized constant)
shadow = pf.call('h*cos(pi*theta/180)')
for h in [15, 30]:
	for t in range(90, 75, -5):
		length = shadow(h=h, theta=t)
		print('shadow({h}, {theta}) = {length}'.format(
				h=h,
				theta=t,
				length=length)
		)
	print(' ')
