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
n_Zmean=100
n_Zvar=15
n_Cstmean=100
n_Cstvar=15
var_ratio=1.1
n_Cmean=100
n_Cvar=15

def interp_low_bound(x, ticks):
    """
    Binary search to find the largest index low_bound such that
    ticks[low_bound] <= x < ticks[low_bound + 1].
    """
    low_bound, up_bound = 0, len(ticks) - 1

    while low_bound + 1 != up_bound:
        mid = (low_bound + up_bound) // 2
        if x < ticks[mid]:
            up_bound = mid
        else:
            low_bound = mid

    return low_bound

def interp_weight(x, ticks, low_bound):
    """
    Computes the interpolation weight for x relative to
    ticks[low_bound] and ticks[low_bound + 1].
    """
    SMALL = 1e-10  # Small constant to avoid division by zero
    denominator = max(ticks[low_bound + 1] - ticks[low_bound], SMALL)
    weight = (x - ticks[low_bound]) / denominator

    # Clamp weight between 0 and 1
    return max(0.0, min(weight, 1.0))

def retrieve(ticks, i, w):
    """
    Perform linear interpolation between ticks[i] and ticks[i+1]
    based on the weight w.

    Parameters:
    ticks (list or numpy array): Array of known values.
    i (int): Lower bound index.
    w (float): Interpolation weight (0 ≤ w ≤ 1).

    Returns:
    float: Interpolated value.
    """
    return ticks[i] * (1.0 - w) + ticks[i + 1] * w

def bilinear_interpolate(f, l1, l2, w1, w2):
    """
    Perform bilinear interpolation for a 2D grid.

    Parameters:
    grid (2D numpy array): Known function values at grid points.
    i (int): Lower bound index along x-axis.
    j (int): Lower bound index along y-axis.
    wx (float): Interpolation weight along x (0 ≤ wx ≤ 1).
    wy (float): Interpolation weight along y (0 ≤ wy ≤ 1).

    Returns:
    float: Interpolated value.
    """
    # Step 1: Interpolate along x for both y positions
    f_11 = f[l1, l2] * (1 - w1) + f[l1+1, l2] * w1
    f_12 = f[l1, l2+1] * (1 - w1) + f[l1+1, l2+1] * w1

    # Step 2: Interpolate along y using the results from Step 1
    f_int = f_11 * (1 - w2) + f_12 * w2

    return f_int 


def int_dZdCst(n_Zmean=n_Zmean,n_Zvar=n_Zvar, n_Cstmean=n_Cstmean,n_Cstvar=n_Cstvar,var_ratio=var_ratio, n_Cmean=n_Cmean,n_Cvar=n_Cvar,):
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
    
    C_mean_max=np.max(table[C_index])
    C_means=np.linspace(0, 1, n_Cmean)*C_mean_max
    C_vars=np.zeros(n_Cvar)
    
    
    C_var_index=variables.index("ProgressVariableVariance")
    C_var_max=np.max(table[C_var_index])
    print("max cv",C_var_max)
    for i in range(n_Cvar-1):
        C_vars[i+1]=(1-var_ratio**(i+1))/(1-var_ratio)
    C_vars=(C_vars/C_vars[-1])*C_var_max
    print(C_vars)
    
    etable=np.zeros((n_variables+extra_variables,n_Zmean,n_Zvar,n_Cmean,n_Cvar))
    lbcs=np.zeros((n_Zmean,n_Zvar,n_Cmean,n_Cvar),dtype=int)
    wcs=np.zeros((n_Zmean,n_Zvar,n_Cmean,n_Cvar))
    lbcvs=np.zeros((n_Zmean,n_Zvar,n_Cmean,n_Cvar),dtype=int)
    wcvs=np.zeros((n_Zmean,n_Zvar,n_Cmean,n_Cvar))
    
    l=np.zeros(n_Cstmean,dtype=int)
    w=np.zeros(n_Cstmean)
    f_c_lm=np.zeros(n_Cstmean)
   
    for mz in range(n_Zmean):
            for vz in range(n_Zvar):
              f_cv=table[C_var_index][mz][vz]
              for mc in range(n_Cmean):
                for vc in range(n_Cvar):
                 for cst_ind in range(n_Cstmean):
                  f_cv_lv=f_cv[cst_ind]
                  #print("Cv",C_vars[vc])
                  #print("f_cv_lv",f_cv_lv)
                  if(vc==0):
                      l[cst_ind]=0
                      w[cst_ind]=0
                  else:
                      l[cst_ind]=interp_low_bound(C_vars[vc],f_cv_lv)
                      w[cst_ind]=interp_weight(C_vars[vc],f_cv_lv,l[cst_ind])
                  #print("l ",l[cst_ind]," w ",w[cst_ind])
                   
                  f_c_lv=table[C_index][mz][vz][cst_ind]
                  f_c_lm[cst_ind]=retrieve(f_c_lv, l[cst_ind], w[cst_ind])
                 #print("f_c_l_m ",f_c_lm) 
                 
                 lbcs[mz,vz,mc,vc]=interp_low_bound(C_means[mc],f_c_lm)
                 #print("Cmean",C_means[mc])
                 #print("f_c_l_m ",f_c_lm)
                 #print("lb_cst",lbcs[mz,vz,mc,vc])
                 wcs[mz,vz,mc,vc]=interp_weight(C_means[mc],f_c_lm,lbcs[mz,vz,mc,vc])
                 #print("w_cst",wcs[mz,vz,mc,vc])                 
                 f_cv_lv2= table[C_var_index][mz][vz][lbcs[mz,vz,mc,vc]]*(1-wcs[mz,vz,mc,vc]) + table[C_var_index][mz][vz][lbcs[mz,vz,mc,vc]+1]*wcs[mz,vz,mc,vc]
                 #print("lb f_cv_lv2",table[C_var_index][mz][vz][lbcs[mz,vz,mc,vc]])
                 #print("f_cv_lv2 ",f_cv_lv2) 
                 
                 #print("Cv",C_vars[vc])
                 lbcvs[mz,vz,mc,vc]=interp_low_bound(C_vars[vc],f_cv_lv2)
                 #print("lb_cvar",lbcvs[mz,vz,mc,vc])
                 wcvs[mz,vz,mc,vc]=interp_weight(C_vars[vc],f_cv_lv2,lbcvs[mz,vz,mc,vc])
                 #print("w_cvar",wcvs[mz,vz,mc,vc])
    
    for v in range(n_variables+extra_variables):
        for mz in range(n_Zmean):
            for vz in range(n_Zvar):
              for mc in range(n_Cmean):
                for vc in range(n_Cvar):

                             
                  etable[v][mz][vz][mc][vc]=bilinear_interpolate(table[v][mz][vz], lbcs[mz,vz,mc,vc], lbcvs[mz,vz,mc,vc],wcs[mz,vz,mc,vc], wcvs[mz,vz,mc,vc]) 
                  #if v==C_index:
                   #     print("mc",mc)
                    #    print("value",etable[v][mz][vz][mc][vc])
                   
                 
                
                
                
    
    
    
    axes = ["variables", "ZAverage", "ZNormalizedVariance", "ProgressVariableAverage","ProgressVariableVariance"] 
     #go to parent directory
    os.chdir('..')


    

    with h5py.File(output_file, "w") as f:
        # Create the main dataset
        etable = f.create_dataset("flameletTable", data=etable)

        # Create axes datasets and attach scales
        dt = h5py.string_dtype(encoding='utf-8')
        f.create_dataset(axes[0], data=np.array(variables, dtype=dt))  # Variables
        f.create_dataset(axes[1], data=Z_means)  # Zmean
        f.create_dataset(axes[2], data=Z_vars)  # Zvar
        f.create_dataset(axes[3], data=C_means)  # Cstmean
        f.create_dataset(axes[4], data=C_vars)  # Cstvar

        # Attach axis labels and scales
        for i, axis in enumerate(axes):
            etable.dims[i].label = axis
            f[axis].make_scale(axis)
            etable.dims[i].attach_scale(f[axis])

    print(f"HDF5 file successfully saved as '{output_file}'",flush=True)

    return


if __name__ == "__main__":
    int_dZdCst()


        

    
    
    
    
  
       
        
    
