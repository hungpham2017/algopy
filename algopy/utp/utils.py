import numpy
from algopy.utp.utps import UTPS
from algopy.utp.utpm import UTPM


def utpm2utps(x):
    """
    converts an instance of UTPM with  x.tc.shape = P,D,N,M
    to a (N,M) array of UTPS instances y_ij, where y_ij.tc.shape = (P,D)
    """
    P,D,N,M = x.tc.shape
    
    tmp_n = []
    for n in range(N):
        tmp_m = []
        for m in range(M):
            tmp_m.append( UTPS(x.tc[:,:,n,m]))
        tmp_n.append(tmp_m)
    
    return numpy.array(tmp_n)
    
    
def utps2utpm(x):
    """
    converts a 2D array x of UTPS instances with x.shape = (N,M)
    and x_ij.tc.shape = (D,P)
    to a UTPM instance y where y.tc.shape = (D,P,N,M)
    
    if x is a 1D array it is converted to a (D,P,N,1) matrix
    
    """
    
    if numpy.ndim(x) == 1:
        x = numpy.reshape(x, (numpy.size(x),1))
    
    N,M = numpy.shape(x)
    P,D = numpy.shape(x[0,0].tc)
    
    tmp = numpy.zeros((P,D,N,M),dtype=float)
    
    for n in range(N):
        for m in range(M):
            tmp[:,:,n,m] = x[n,m].tc[:,:]
    
    return UTPM(tmp)
    
    
    
