import numpy as np
import numpy.polynomial.polynomial as P
from scipy.stats import beta
from scipy.interpolate import interp1d
import scipy as sp

# calculate the beta pdf coefficients alpha and beta(from mean and variance)
def beta_coef(ave, var):

    a = ave*(1./var-1.)
    b = (1.-ave)*(1./var-1.)

    return a, b


# analytic integration with beta pdf, with linear fit of the target function
#This returns the integral f(x)p(x)dx
def beta_integration_analytic(f, x,x_ave,x_nvar):
    # z1_index = index = np.where(x == 1.0)[0][0]
    # x=x[:z1_index+1]
    # f=f[:z1_index+1]
    a, b = beta_coef(x_ave, x_nvar)
     
    rv0 = beta(a, b) #creates a beta function object with the coeffs
    cdf0 = rv0.cdf(x) #cumulative distribution function ( P(X<=x) )
    B0 = sp.special.beta(a, b)#scaling to ensure probability of 1
    
    #creates a beta function object with the one coeff shifted
    rv1 = beta(a+1., b)
    cdf1 = rv1.cdf(x)
    B1 = sp.special.beta(a+1, b)

    B = B1/B0

    c0 = np.zeros_like(x)
    c1 = np.zeros_like(x)
    cl1=np.diff(f)/np.diff(x)
    cl0=f[:-1]-cl1*x[:-1]
    
    c0[:-1] -= cl0
    c0[1:] += cl0

    c1[:-1] -= cl1
    c1[1:] += cl1

    

    c1 *= B

    return np.sum(c0*cdf0+c1*cdf1)


# integration with the delta pdf, implemented as a linear interp
def delta_integration(f, x, x_ave):

    y = interp1d(x, f, kind='linear')

    return np.float64(y(x_ave))


# integration with the bimodal pdf
def bimodal_integration(f, x_ave):

    return f[0]*(1.-x_ave)+f[-1]*x_ave

#x_nvar is normalised var
# beta integration of one average and one variance(different limits are treated depending on mean and variance)

def beta_integration(f, x, x_ave, x_nvar,EPS=1e-9):

    if x_ave < EPS:#as x_ave->0, it becomes delta concentrated at x=0
        return f[0]
    
    elif x_ave > 1.-EPS:#as x_ave->1, it becomes delta concentrated at x=1
        return f[-1]
    elif x_nvar < EPS: #as x_nvar->0, it becomes delta concentrated at x=x_ave
        return delta_integration(f, x, x_ave)
    elif x_nvar > 1.-EPS: #as x_nvar->1, it becomes like delta at x=0 and x=1 with the area under it in the ratio (1-x_ave) and x_ave
        return bimodal_integration(f, x_ave)
    else:
        return beta_integration_analytic(
                f, x,x_ave,x_nvar)








