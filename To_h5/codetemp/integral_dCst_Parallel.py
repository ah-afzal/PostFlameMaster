import numpy as np
import numpy.polynomial.polynomial as P
from scipy.stats import beta
from scipy.interpolate import interp1d
import scipy as sp
import pandas as pd
from Beta_Integral import beta_integration
import re


def int_dCst(fs,Csts,pool,n_Cstmean=50,n_Cstvar=7,var_ratio=1.1):
    #obtain c_st vale   

    
    Cst_means = np.linspace(0, 1, n_Cstmean)
    Cst_vars=np.zeros(n_Cstvar)
    for i in range(n_Cstvar-1):
        Cst_vars[i+1]=(1-var_ratio**(i+1))/(1-var_ratio)
    Cst_vars=Cst_vars/Cst_vars[-1] 

    proc_inputs = [
            (fs[:,i], np.array(Csts), Cst_means[xx], Cst_vars[yy])
    for i in range(fs.shape[1])
    for xx in range(n_Cstmean)
    for yy in range(n_Cstvar)
                  ]
    #with Pool(core_count) as p:
    output= pool.starmap(beta_integration,proc_inputs)
     
    resh_output=np.array(output).reshape(fs.shape[1],n_Cstmean,n_Cstvar) 
    return resh_output
    

    
