import pandas as pd
import numpy as np
import os
from integral_dCst_Parallel import int_dCst
from integral_dZ_Parallel import int_dZ
import itertools
from Beta_Integral import beta_integration
import h5py
from multiprocessing import Pool
from tqdm import tqdm

core_count = 192
n_Zmean=10
n_Zvar=5
n_Cstmean=10
n_Cstvar=5
var_ratio=1.1

def int_dZdCst(n_Zmean=n_Zmean,n_Zvar=n_Zvar, n_Cstmean=n_Cstmean,n_Cstvar=n_Cstvar,var_ratio=var_ratio):
    directory = 'Modified_Files'
    directs=os.listdir(directory)
    os.chdir(directory)  
    output_file='flameletTable.h5'
    integral_dZ={} #stores integrals wrt Z, with key = Cst
    i=1
    with Pool(core_count) as p:
        
     print("Starting dZ integration",flush=True)
     for filename in directs:
            
        print(i," out of ", len(directs),flush=True)
        integral=int_dZ(filename,p,n_Zmean,n_Zvar)
        integral_dZ[integral[0]]=integral[1]#0:Cst,1:Integrals with three index(variable,mean and var),2:variable names
        i+=1
    
     dict_sorted=sorted(integral_dZ)#sort keys(C_st) of dictionary. This doesn't change the dictionary
     #dictionary modified to scale C_st b/w 0 and 1
     modified_dict = {(key - dict_sorted[0]) / (dict_sorted[-1]-dict_sorted[0]): value for key, value in integral_dZ.items()}
    
     #create list of means and variances
     Cst_means = np.linspace(0, 1, n_Cstmean)
     Cst_vars=np.zeros(n_Cstvar)
     for i in range(n_Cstvar-1):
       Cst_vars[i+1]=(1-var_ratio**(i+1))/(1-var_ratio)
     Cst_vars=Cst_vars/Cst_vars[-1]
     #sorted list of modified_dict keys
     mod_sort=sorted(modified_dict.keys())


    
     n_variables=integral[1].shape[0] #extracts number of variables
     n_Zmean=integral[1].shape[1]#extracts number of Zmeans
     n_Zvar=integral[1].shape[2]#extracts number of Zvars
     variables=integral[2] # gets the variable names
     #final table with index: [var index][Zmean][Zvar][Cstmean][Cstvar]
     #add C_var and Mean_C_resWC_res
     extra_variables=2
     variables.append('ProgressVariableVariance')
     variables.append('MeanCresWCres')
          
    
     table=np.zeros((n_variables+extra_variables,n_Zmean,n_Zvar,n_Cstmean,n_Cstvar))
    
     C_index=variables.index('ProgressVariable')
     WC_index=variables.index('ProdRateProgressVariable')
     C2_index=variables.index('SquareProgVar')
     CWC_index=variables.index('ProgVarProdRate') #This is progvar*progvarproductionrate
       
    
     print("Starting dCst integration",flush=True)
     
     ct=1
     for mz in range(n_Zmean):
        print(ct," out of ",n_Zmean,flush=True)
        ct+=1
        for vz in range(n_Zvar):
           integrand=np.array([modified_dict[_][:,mz,vz] for _ in mod_sort])
           print(integrand[:,12])
           table[:-2,mz,vz,:,:]=int_dCst(integrand,np.array(mod_sort),p,n_Cstmean,n_Cstvar,var_ratio)
       

     
    for v in range(n_variables,n_variables+extra_variables):
        for mz in range(n_Zmean):
            for vz in range(n_Zvar):
              for mc in range(n_Cstmean):
                for vc in range(n_Cstvar):
               
                        if variables[v]=='ProgressVariableVariance':
                            C_mean=table[C_index][mz][vz][mc][vc]
                            C2_mean=table[C2_index][mz][vz][mc][vc]
                            table[v][mz][vz][mc][vc]=C2_mean-C_mean**2
                            continue
                        if variables[v]=='MeanCresWCres':
                            C_mean=table[C_index][mz][vz][mc][vc]
                            WC_mean=table[WC_index][mz][vz][mc][vc]
                            CWC_mean=table[CWC_index][mz][vz][mc][vc]
                            
                            table[v][mz][vz][mc][vc]=CWC_mean-C_mean*WC_mean
                            continue
                            
                            
                            
    Z_means = np.linspace(0, 1, n_Zmean)
    Z_vars=np.zeros(n_Zvar)
    for i in range(n_Zvar-1):
        Z_vars[i+1]=(1-var_ratio**(i+1))/(1-var_ratio)
    Z_vars=Z_vars/Z_vars[-1]
    axes = ["variables", "ZAverage", "ZNormalizedVariance", "ParameterProgressVariableAverage","ParameterProgressVariableNormalizedVariance"] 
     #go to parent directory
    os.chdir('..')




    with h5py.File(output_file, "w") as f:
        # Create the main dataset
        table = f.create_dataset("flameletTable", data=table)

        # Create axes datasets and attach scales
        dt = h5py.string_dtype(encoding='utf-8')
        f.create_dataset(axes[0], data=np.array(variables, dtype=dt))  # Variables
        f.create_dataset(axes[1], data=Z_means)  # Zmean
        f.create_dataset(axes[2], data=Z_vars)  # Zvar
        f.create_dataset(axes[3], data=Cst_means)  # Cstmean
        f.create_dataset(axes[4], data=Cst_vars)  # Cstvar

        # Attach axis labels and scales
        for i, axis in enumerate(axes):
            table.dims[i].label = axis
            f[axis].make_scale(axis)
            table.dims[i].attach_scale(f[axis])

    print(f"HDF5 file successfully saved as '{output_file}'",flush=True)

    return


if __name__ == "__main__":
    int_dZdCst()


        

    
    
    
    
  
       
        
    
