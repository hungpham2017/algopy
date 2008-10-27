#!/usr/bin/env python
"""
Author: Sebastian Walter, HU Berlin
Package: Simple Python implementation of Algorithmic Differentiation (adouble) in forward mode

example usage: Newton's method

from AD import *

def f(x):
	return x*x

def Newton_iteration(x,f):
	ax = adouble(x, 1.)
	af = f(ax)
	return x - af.tc/af.dx

x_old = 3.
while True:
	x_new = Newton_iteration(x_old,f)
	print x_new
	if abs(x_old - x_new) < 0.0001:
		break
	x_old = x_new
"""
import numpy as npy
import networkx as nx

class Ops:
	add = 0
	mul = 1
	sub = 2
	div = 3

class adouble:
	"""Class: Algorithmic differentiation"""

	def __init__(self, *taylor_coeffs):
		"""Constructor takes a list, array, tuple and variable lenght input"""
		if not npy.isscalar(taylor_coeffs[0]):
			taylor_coeffs = npy.array(taylor_coeffs[0],dtype=float)
		self.tc = npy.array(taylor_coeffs,dtype=float)
		self.off = 0
		self.d = npy.shape(self.tc)[0]

	def get_tc(self):
		return self.tc
	def set_tc(self,x):
		self.tc[:] = x[:]

	tc = property(get_tc, set_tc)

	def copy(self):
		return adouble(self.tc)


	def __pow__(self, exponent):
		"""Computes the power: x^n, where n must be an int"""
		if isinstance(exponent, int):
			tmp = 1
			for i in range(exponent):
				tmp=tmp*self
			return tmp
		else:
			raise TypeError("Second argumnet must be an integer")

	def __add__(self, rhs):
		"""compute new Taylorseries of the function f(x,y) = x+y, where x and y adouble objects"""
		tmp = adouble(self.tc)
		if isinstance(rhs, adouble):
			tmp.tc += rhs.tc

			return tmp
		elif npy.isscalar(rhs):
			tmp.tc[0] += rhs
			return tmp
		else:
			raise NotImplementedError

	def __radd__(self, val):
		return self+val

	def __sub__(self, rhs):
		tmp = self.copy()
		if isinstance(rhs, adouble):
			tmp.tc -= rhs.tc
			return tmp
		elif npy.isscalar(rhs):
			tmp.tc[0] -= rhs
			return tmp
		else:
			raise NotImplementedError

	def __rsub__(self, other):
		return -self + other

	def __mul__(self, rhs):
		"""compute new Taylorseries of the function f(x,y) = x*y, where x and y adouble objects"""
		if isinstance(rhs, adouble):
			return adouble(npy.array(
					[ npy.sum(self.tc[:k+1] * rhs.tc[k::-1]) for k in range(self.d)]
					))
		elif npy.isscalar(rhs):
			return adouble(rhs * self.tc)
		else:
			raise NotImplementedError("%s multiplication with adouble object" % type(rhs))

	def __rmul__(self, val):
		return self*val

	def __div__(self, rhs):
		"""compute new Taylorseries of the function f(x,y) = x/y, where x and y adouble objects"""
		if isinstance(rhs, adouble):
			y = adouble(npy.zeros(d))
			for k in range(self.d):
				y.tc[k] = 1./ rhs.tc[0] * ( self.tc[k] - npy.sum(y[:k] * rhs.tc[k-1::-1]))
			return y
		else:
			return self*(1/float(val))

	def __rdiv__(self, val):
		return adouble(val)/self

	def __neg__(self):
		return adouble(-self.tc)


	def __str__(self):
		"""human readable representation of the adouble object for printing >>print adouble([1,2,3]) """
		return 'a(%s)'%str(self.tc)

	def __repr__(self):
		""" human readable output of the adouble object or debugging adouble([1,2,3]).__repr__()"""
		return 'adouble object with taylor coefficients %s'%self.tc

	def sqrt(self):
		y = adouble(npy.zeros(self.d))
		y.tc[0] = npy.sqrt(self.tc[0])
		for k in range(1,self.d):
			y.tc[k] = 1./(2*y.tc[0]) * ( self.tc[k] - npy.sum( y.tc[1:k] * y.tc[k-1:1:-1]))
		return y

	def __abs__(self):
		tmp = self.copy()
		if tmp.tc[0] >0:
			pass
		elif tmp.tc[0] < 0:
			tmp.tc[1:] = -tmp.tc[1:]
		else:
			raise NotImplementedError("differentiation of abs(x) at x=0")
		return tmp