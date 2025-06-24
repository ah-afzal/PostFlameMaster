import numpy as np
import numpy.polynomial.polynomial as P
from scipy.stats import beta
from scipy.interpolate import interp1d
import scipy as sp
import pandas as pd
from Beta_Integral import beta_integration
import re


def int_dZ(file_path,pool,n_Zmean=100,n_Zvar=15,var_ratio=1.1):
    #obtain c_st vale   
    c_st=float(re.findall(r"\d+\.\d+", file_path)[-1])
    
    df = pd.read_csv(file_path) #read the data
    data_dict = df.to_dict(orient='list')#convert excel to dictionary
    Z=data_dict['Z'] #we have f(Z)
    #del data_dict['Z']
    
    #create list of means and variances
    Z_means = np.linspace(0, 1, n_Zmean)
    Z_vars=np.zeros(n_Zvar)
    for i in range(n_Zvar-1):
        Z_vars[i+1]=(1-var_ratio**(i+1))/(1-var_ratio)
    Z_vars=Z_vars/Z_vars[-1]
    
    
    #gets the variable names
    keys = list(data_dict.keys()) 

    #Create integer keys
    integer_keys = np.arange(len(keys))
    integral_vars=np.zeros((len(keys),n_Zmean,n_Zvar)) #integrated variables
    proc_inputs = [
    (np.array(data_dict[keys[i]]), np.array(Z), Z_means[xx], Z_vars[yy])
    for i in integer_keys
    for xx in range(n_Zmean)
    for yy in range(n_Zvar)
                  ]
    #with Pool(core_count) as p:
    output= pool.starmap(beta_integration,proc_inputs)
     
    resh_output=np.array(output).reshape(len(keys),n_Zmean,n_Zvar) 
    return [c_st,resh_output,keys]
    

    
