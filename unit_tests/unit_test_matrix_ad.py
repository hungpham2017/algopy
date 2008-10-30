#!/usr/bin/env python
import sys
import numpy
import numpy.linalg
from numpy import *

sys.path = ['..'] + sys.path
from matrix_ad import *

def test_trace_forward():
	x = Mtc(ones((2,2)),ones((2,2)))
	y = x.trace()
	assert trace(x.X) == y.X[0,0] and trace(x.Xdot) == y.Xdot[0,0]

def test_1x1dot1x1_reverse():
	"""
	f = x.dot(y)  x and are (1,1)-arrays
	x = 1
	y = 2

	therefore 
	grad f = [2,1].T
	hess f = [[0,1],[1,0]]
	"""
	cg = CGraph()
	Fq = [Function(Mtc([[1.]],[[1.]])), Function(Mtc([[2.]],[[0.]]))]
	#zer = Mtc(array([[0.]]))
	#Fzer = Function(zer)

	FR = Fq[0].dot(Fq[1])

	cg.independentFunctionList = Fq
	cg.dependentFunctionList = [FR]
	cg.reverse([Mtc([[1.]])])

	# check gradient
	assert Fq[0].xbar.X[0,0] == 2
	assert Fq[1].xbar.X[0,0] == 1

	#check first column of the hessian
	assert Fq[0].xbar.Xdot[0,0] == 0
	assert Fq[1].xbar.Xdot[0,0] == 1

def test_2x2dot2x2_reverse():
	"""
	C = A.dot(B)  A,B are (2,2)-arrays
	"""
	A =    array([[3.,1.],[2.,4.]])
	Adot = array([[1.,0.],[0.,0.]])
	B =    array([[5.,2.],[1.,7.]])
	Bdot = array([[0.,0.],[0.,0.]])
	C = numpy.dot(A,B)
	Cdot = numpy.dot(A,Bdot) + numpy.dot(Adot,B)
	
	Cbar = array([[1.,0.],[0.,0.]])
	
	cg = CGraph()
	FA = Function(Mtc(A,Adot))
	FB = Function(Mtc(B,Bdot))

	FC = FA.dot(FB)

	cg.independentFunctionList = [FA,FB]
	cg.dependentFunctionList = [FC]
	cg.reverse([Mtc(Cbar)])

	# forward evaluation
	assert numpy.prod(C == FC.x.X)
	assert numpy.prod(Cdot == FC.x.Xdot)

	# reverse evaluation
	assert numpy.prod(FA.xbar.X == dot(B,Cbar))
	assert numpy.prod(FB.xbar.X == dot(Cbar,A))
	#assert False # FA.xbar.Xdot has to be verified
	#assert False # FB.xbar.Xdot has to be verified

def test_matrix_assembly_2x2():
	"""
	C = [[A,B],[B,A]]
	A,B are (2,2)-arrays
	"""
	A =    array([[1.,1.],[1.,1.]])
	Adot = array([[2.,2.],[2.,2.]])
	B =    array([[3.,3.],[3.,3.]])
	Bdot = array([[4.,4.],[4.,4.]])

	C = zeros((4,4))
	C[:2,:2] = A
	C[:2,2:] = B
	C[2:,:2] = B
	C[2:,2:] = A

	Cdot = zeros((4,4))
	Cdot[:2,:2] = Adot
	Cdot[:2,2:] = Bdot
	Cdot[2:,:2] = Bdot
	Cdot[2:,2:] = Adot

	Cbar = 5*ones((4,4))
	Cbardot = 6*ones((4,4))

	cg = CGraph()
	FA = Function(Mtc(A,Adot))
	FB = Function(Mtc(B,Bdot))

	FC = Function([[FA,FB],[FB, FA]])

	cg.independentFunctionList = [FA,FB]
	cg.dependentFunctionList = [FC]
	cg.reverse([Mtc(Cbar,Cbardot)])

	# forward evaluation
	assert numpy.prod(FC.x.X == C)
	assert numpy.prod(FC.x.Xdot == Cdot)

	# reverse evaluation
	assert numpy.prod(FA.xbar.X == 2*FC.xbar[:2,:2].X)
	assert numpy.prod(FB.xbar.X == 2*FC.xbar[2:,2:].X)
	
	assert numpy.prod(FA.xbar.Xdot == 2*FC.xbar[:2,:2].Xdot)
	assert numpy.prod(FB.xbar.Xdot == 2*FC.xbar[2:,2:].Xdot)

def test_plot_computational_graph():
	A =    array([[11.,1.],[12.,1.]])
	Adot = array([[2.,2.],[2.,2.]])
	B =    array([[31.,3.],[3.,32.]])
	Bdot = array([[4.,4.],[4.,4.]])

	C = zeros((4,4))
	C[:2,:2] = A
	C[:2,2:] = B
	C[2:,:2] = B
	C[2:,2:] = A

	Cdot = zeros((4,4))
	Cdot[:2,:2] = Adot
	Cdot[:2,2:] = Bdot
	Cdot[2:,:2] = Bdot
	Cdot[2:,2:] = Adot

	Cbar = 5*ones((4,4))
	Cbardot = 6*ones((4,4))

	cg = CGraph()
	FA = Function(Mtc(A,Adot))
	FB = Function(Mtc(B,Bdot))

	FA = FA*FB
	FA = FA.dot(FB) + FA.transpose()
	FA = FB + FA * FB
	FB = FA.inv()
	FB = FB.transpose()

	FC = Function([[FA,FB],[FB, FA]])
	
	FTR = FC.trace()
	cg.plot(filename = 'trash/computational_graph.png', method = 'circo' )
	cg.plot(filename = 'trash/computational_graph_circo.svg', method = 'circo' )
	cg.plot(filename = 'trash/computational_graph_dot.svg', method = 'dot' )


def test_inverse_2x2():
	A =    array([[3.,0.],[0.,7.]])
	Adot = array([[1.,0.],[0.,0.]])
	cg = CGraph()
	FA = Function(Mtc(A,Adot))
	Finv = FA.inv()
	Cbar = eye(2)
	cg.independentFunctionList = [FA]
	cg.dependentFunctionList = [Finv]
	cg.reverse([Mtc(Cbar)])
	C = inv(A)
	assert numpy.prod( numpy.linalg.inv(A) == Finv.x.X )
	assert numpy.prod( dot(dot(C,Cbar),C) == FA.xbar.X)
	
def test_trace_2x2():
	"""
	"""
	A =    array([[1.,1.],[1.,1.]])
	Adot = array([[2.,2.],[2.,2.]])
	trbar = array([[13.]])
	trbardot = array([[0.]])
	
	cg = CGraph()
	FA = Function(Mtc(A,Adot))
	Ftr = FA.trace()
	cg.independentFunctionList = [FA]
	cg.dependentFunctionList = [Ftr]
	cg.reverse([Mtc(trbar,trbardot)])


	assert numpy.prod( FA.xbar.X == array([[13.,0.],[0.,13.]]))
	


def test_newtons_method():
	"""
	min_q Phi(C(q))

	Phi(C) = trace(C)
	C = [[q1**2, 0], [0 ,q2**2 ]]

	staring point: (13.,17.)
	solution: (0.,0.)

	Newton's method with full steps should converge in one step
	"""

	H = zeros((2,2))
	g = zeros((2,2)) # first column, gradient of first direct. derv., second second direct. derv, should be the same

	for n in range(2):
		# directional derivatives to evaluate columns of the hessian
		q1 = array([[13.]])
		q2 = array([[17.]])
		ze = array([[0.]])

		q1dot = array([[1.*(n==0)]])
		q2dot = array([[1.*(n==1)]])

		zedot = array([[0.]])

		cg = CGraph()
		Fq1 = Function(Mtc(q1, q1dot))
		Fq2 = Function(Mtc(q2, q2dot))
		Fze = Function(Mtc(ze, zedot))
		FC = Function([[Fq1*Fq1,Fze],[Fze,Fq2*Fq2]])
		FPhi = FC.trace()

		Phibar = array([[1.]])
		Phibardot = array([[0.]])
		
		cg.independentFunctionList = [Fq1,Fq2]
		cg.dependentFunctionList = [FPhi]
		cg.reverse([Mtc(Phibar, Phibardot)])
		
		
		g[0,n] = Fq1.xbar.X[0,0]
		g[1,n] = Fq2.xbar.X[0,0]
		H[0,n] = Fq1.xbar.Xdot[0,0]
		H[1,n] = Fq2.xbar.Xdot[0,0]



	# compute new search direction
	delta_q = numpy.linalg.solve(H,-g[:,0])
	q_plus = [13.,17.] + delta_q
	assert numpy.prod(q_plus == [0.,0.])

	


	

if __name__ == "__main__":
	#q = [Mtc([[1.]],[[1.]]), Mtc([[2.]],[[0.]])]
	
	#C = [[q[0],zer],[zer,q[1]]]

	cg = CGraph()
	Fq = [Function(Mtc([[3.,1.],[2.,4.]],[[1.,0.],[0.,0.]])),
	      Function(Mtc([[5.,2.],[1.,7.]],[[0.,0.],[0.,0.]]))]

	FR = Fq[0].dot(Fq[1])
	FT = FR.trace()

	cg.independentFunctionList = Fq
	cg.dependentFunctionList = [FT]
	cg.reverse([Mtc([[1.]])])

	print cg

	#zer = Mtc(array([[0.]]))
	#Fzer = Function(zer)
	#FC = Function([[Fq[0],Fzer],[Fzer, Fq[1]]])

	#print 'FC=',FC
	#FTR = FC.trace()


	#x = array([[Tc([1.,0.]), Tc([2.,0.])]])
	#y = convert_from_tc_to_mtc(x)

	#print 'x=',x
	#print 'y=',y
	
	
