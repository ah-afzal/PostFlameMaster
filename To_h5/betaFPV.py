import pandas as pd
import numpy as np
import os
from integral_dZ import int_dZ
import itertools
from Beta_Integral import beta_integration
import h5py

def int_dZdCst(n_Cstmean=5,n_Cstvar=3,var_ratio=1.1):
    directory = 'Modified_Files'
    directs=os.listdir(directory)
    os.chdir(directory)  
    output='flameletTable.h5'
    integral_dZ={} #stores integrals wrt Z, with key = Cst
    i=1
    for filename in directs:
        
        print("filenumber : ",i)
        integral=int_dZ(filename)
        integral_dZ[integral[0]]=integral[1]#0:Cst,1:Integrals with three index(variable,mean and var),2:variable names
        i+=1
    
    dict_sorted=sorted(integral_dZ)#sort keys(C_st) of dictionary
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
    print(mod_sort)
    
    n_variables=integral[1].shape[0] #extracts number of variables
    n_Zmean=integral[1].shape[1]#extracts number of Zmeans
    n_Zvar=integral[1].shape[2]#extracts number of Zvars
    variables=integral[2] # gets the variable names
    #final table with index: [var index][Zmean][Zvar][Cstmean][Cstvar]
    #add C_var and Mean_C_resWC_res
    extra_variables=2
    variables.append('Cvar')
    variables.append('MeanCresWCres')
   
    
    table=np.zeros((n_variables+extra_variables,n_Zmean,n_Zvar,n_Cstmean,n_Cstvar))
    
    C_index=variables.index('ProgressVariable')
    WC_index=variables.index('ProdRateProgressVariable')
    C2_index=variables.index('SquareProgVar')
    CWC_index=variables.index('ProgVarProdRate')
       
    
    
    
    for v in range(n_variables+extra_variables):
        for mz in range(n_Zmean):
            for vz in range(n_Zvar):
              for mc in range(n_Cstmean):
                for vc in range(n_Cstvar):
               
                        print(v,mz,vz,mc,vc)
                        if variables[v]=='Cvar':
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
                            
                            
                            
                        integrand=np.array([modified_dict[cst_norm][v][mz][vz]  for cst_norm in mod_sort])
                        table[v][mz][vz][mc][vc]=beta_integration(integrand,np.array(mod_sort),Cst_means[mc],Cst_vars[vc])
                        
                            
    Z_means = np.linspace(0, 1, n_Zmean)
    Z_vars=np.zeros(n_Zvar)
    for i in range(n_Zvar-1):
        Z_vars[i+1]=(1-var_ratio**(i+1))/(1-var_ratio)
    Z_vars=Z_vars/Z_vars[-1]
    
    axes = ['variables','Zmean','Zvar','Cstmean','Cstvar']
    #go to parent directory
    os.chdir('..')
    with h5py.File(output, 'w') as f:
        
        f['flameletTable'] = table
        
        # strings
        dt = h5py.special_dtype(vlen=str)
        ds = f.create_dataset(axes[0],
                              len(variables),
                              dtype=dt)
        ds[...] =variables


       
        f[axes[1]] = Z_means
        f[axes[2]] = Z_vars
        f[axes[3]] = Cst_means
        f[axes[4]] = Cst_vars
        
        

        for i, v in enumerate(axes):
            f['flameletTable'].dims[i].label = v
            #creates a scale before it can be attached
            f[v].make_scale(v)
            #i'th dimension is atatched to f[v] 
            f['flameletTable'].dims[i].attach_scale(f[v])

        

            
    return
if __name__ == "__main__":
    int_dZdCst()


        

    
    
    
    
  
       
        
    