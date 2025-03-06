import pandas as pd
import numpy as np
import os
from integral_dCst_Parallel import int_dCst
import itertools
from Beta_Integral import beta_integration
import h5py
from multiprocessing import Pool
from tqdm import tqdm
from scipy.interpolate import griddata
from matplotlib.path import Path


core_count = 192
n_Zmean=100
n_Zvar=15
n_Cmean=100
n_Cvar=15
var_ratio=1.1
combined_csv="compiled_output.csv"

def int_dC(f,Z,pool,n_Zmean=100,n_Zvar=15,var_ratio=1.1,max_c=1):
    #print("f",f)
    #print("Z",Z)
    Z=Z/Z[-1]
    #create list of means and variances
    Z_means = np.linspace(0, 1, n_Zmean)
    Z_vars=np.zeros(n_Zvar)
    for i in range(n_Zvar-1):
        Z_vars[i+1]=(1-var_ratio**(i+1))/(1-var_ratio)
    Z_vars=Z_vars/Z_vars[-1]

    integral_vars=np.zeros((f.shape[0],n_Zmean,n_Zvar)) #integrated variables
    proc_inputs = [
    (f[i,:], Z, Z_means[xx], Z_vars[yy])
    for i in range(f.shape[0])
    for xx in range(n_Zmean)
    for yy in range(n_Zvar)
                  ]
    #with Pool(core_count) as p:
    output= pool.starmap(beta_integration,proc_inputs)
    resh_output=np.array(output).reshape(f.shape[0],n_Zmean,n_Zvar)
    return resh_output




def int_dZ(f,Z,pool,n_Zmean=100,n_Zvar=15,var_ratio=1.1):
    #print("f",f)
    #print("Z",Z)
    
    #create list of means and variances
    Z_means = np.linspace(0, 1, n_Zmean)
    Z_vars=np.zeros(n_Zvar)
    for i in range(n_Zvar-1):
        Z_vars[i+1]=(1-var_ratio**(i+1))/(1-var_ratio)
    Z_vars=Z_vars/Z_vars[-1]

    integral_vars=np.zeros((f.shape[0],n_Zmean,n_Zvar)) #integrated variables
    proc_inputs = [
    (f[i,:], Z, Z_means[xx], Z_vars[yy])
    for i in range(f.shape[0])
    for xx in range(n_Zmean)
    for yy in range(n_Zvar)
                  ]
    #with Pool(core_count) as p:
    output= pool.starmap(beta_integration,proc_inputs)
    resh_output=np.array(output).reshape(f.shape[0],n_Zmean,n_Zvar) 
    return resh_output

def int_dZdCst(n_Zmean=n_Zmean,n_Zvar=n_Zvar, n_Cmean=n_Cmean,n_Cvar=n_Cvar,var_ratio=var_ratio):
    df = pd.read_csv(combined_csv)
    Z = df['Z'].values
    prog_var="ProgressVariable"
    c = df[prog_var].values 
    max_c = np.max(c)
    
    # Extract dependent variables (all except Z and c)
    dependent_vars = [col for col in df.columns]

    # Define structured grid (100 x 100 points)
    num_points = 150
    Z_grid = np.linspace(0, 1, num_points)  # Structured Z values (still between 0 and 1)
    c_grid = np.linspace(0, max_c, num_points)  # Structured c values (between 0 and max_c)
    # Create meshgrid with 'ij' indexing
    Z_mesh, c_mesh = np.meshgrid(Z_grid, c_grid, indexing='ij')

    # Flatten grid points for easier processing
    grid_points = np.vstack((Z_mesh.ravel(), c_mesh.ravel())).T

    # Check if points are inside the convex hull using inpolygon approach

    # Dictionary to store interpolated functions
    f = {}

    # Interpolate each dependent variable
    for var in dependent_vars:
	    values = df[var].values  # Function values from the dataset
	    
	    # Cubic interpolation
	    cubic_interp = griddata((Z, c), values, (Z_mesh, c_mesh), method='cubic')
	    # Use cubic where valid, otherwise nearest
	    
	    # Store in dictionary
	    f[var] = cubic_interp
    for var in dependent_vars:
        for i in range(num_points):
            for j in range(num_points):
                if np.isnan(f[var][i,j]):
                    f[var][i,j:]=0#f[var][i,j-1]
    
                
                 

    
    variables = list(f.keys())  # Store variable names
    f = np.stack([f[var] for var in variables], axis=0)
    #print(f[var_names.index('T')])
    output_file='flameletTable.h5'
    integral_dZ=np.zeros((num_points,f.shape[0],n_Zmean,n_Zvar))
     #stores integrals wrt Z, with key = c
    with Pool(core_count) as p:
        
     print("Starting dZ integration",flush=True)
     for i in range(num_points) :
        print(i+1," out of ", num_points,flush=True)
        integral_dZ[i,:,:,:]=int_dC(f[:,:,i],Z_grid,p,n_Zmean,n_Zvar)    
    
     #create list of means and variances
     C_means = np.linspace(0, 1, n_Cmean)
     C_vars=np.zeros(n_Cvar)
     for i in range(n_Cvar-1):
       C_vars[i+1]=(1-var_ratio**(i+1))/(1-var_ratio)
     C_vars=C_vars/C_vars[-1]
   
    
     #final table with index: [var index][Zmean][Zvar][Cstmean][Cstvar]
     #add C_var and Mean_C_resWC_res
     extra_variables=2
     variables.append('ProgressVariableVariance')
     variables.append('MeanCresWCres')
          
    
     table=np.zeros((len(variables),n_Zmean,n_Zvar,n_Cmean,n_Cvar))
    
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
           integrand=np.array([integral_dZ[:,i,mz,vz] for i in range(len(variables)-extra_variables)])
           table[:-2,mz,vz,:,:]=int_dC(integrand,c_grid,p,n_Cmean,n_Cvar,var_ratio,max_c)
       

     
    for v in range(len(variables)-extra_variables,len(variables)):
        for mz in range(n_Zmean):
            for vz in range(n_Zvar):
              for mc in range(n_Cmean):
                for vc in range(n_Cvar):
               
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
    axes = ["variables", "ZAverage", "ZNormalizedVariance", "ProgressVariableAverage","ProgressVariableNormalizedVariance"] 
     #go to parent directory
    #os.chdir('..')




    with h5py.File(output_file, "w") as f:
        # Create the main dataset
        table = f.create_dataset("flameletTable", data=table)

        # Create axes datasets and attach scales
        dt = h5py.string_dtype(encoding='utf-8')
        f.create_dataset(axes[0], data=np.array(variables, dtype=dt))  # Variables
        f.create_dataset(axes[1], data=Z_means)  # Zmean
        f.create_dataset(axes[2], data=Z_vars)  # Zvar
        f.create_dataset(axes[3], data=C_means*max_c)  # Cmean
        f.create_dataset(axes[4], data=C_vars)  # Cvar

        # Attach axis labels and scales
        for i, axis in enumerate(axes):
            table.dims[i].label = axis
            f[axis].make_scale(axis)
            table.dims[i].attach_scale(f[axis])

    print(f"HDF5 file successfully saved as '{output_file}'",flush=True)

    return


if __name__ == "__main__":
    int_dZdCst()


        

    
    
    
    
  
       
        
    
