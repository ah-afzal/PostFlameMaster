# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 07:30:25 2025

@author: afzala
"""
from integral_dZ_Parallel import int_dZ
import os
import numpy as np
import h5py
from multiprocessing import Pool
core_count=192
n_Zmean=10
n_Zvar=5
var_ratio=1.1

def compile_hdf5(input_directory, output_file="flameletTable.h5"):
    # Axes definitions
    axes = ["variables", "ZAverage", "ZNormalizedVariance", "ParameterProgressVariableAverage"]

    # Storage for results across all Excel files
    cst_values = []
    all_integral_vars = []
    variable_keys = None
    files=os.listdir(input_directory)
    # Process all Excel files in the input directory
    i=1
    with Pool(core_count) as p:
     for filename in files:
        if filename.endswith(".csv"):
            file_path = os.path.join(input_directory, filename)
            c_st, integral_vars, keys= int_dZ(file_path,p,n_Zmean,n_Zvar,var_ratio)
            # Append the results for the current file
            cst_values.append(c_st)
            all_integral_vars.append(integral_vars)
            print(i, " out of ", len(files))
            i+=1
    variable_keys = keys  # Store variable names from any file (assuming consistent variables)

    # Convert list to numpy arrays for HDF5 storage
    
    cst_values = np.array(cst_values)
    all_integral_vars = np.array(all_integral_vars)
    
    sorted_indices = np.argsort(cst_values)
    cst_values_sorted=cst_values[sorted_indices]
    cst_values_sorted=(cst_values_sorted-cst_values_sorted[0])/(cst_values_sorted[-1]-cst_values_sorted[0])
    all_integral_vars_sorted=all_integral_vars[sorted_indices]
    Z_means = np.linspace(0, 1, n_Zmean)
    Z_vars = np.zeros(n_Zvar)
    for i in range(n_Zvar - 1):
        Z_vars[i + 1] = (1 - var_ratio ** (i + 1)) / (1 - var_ratio)
    Z_vars = Z_vars / Z_vars[-1]
    table_3d = np.stack(all_integral_vars_sorted, axis=-1)
    # Ensure correct dimension ordering
    #all_integral_vars = np.transpose(all_integral_vars_sorted, (1, 2, 3, 0))  # Variables, Zmean, Zvar, Cstmean

    # Write to HDF5
    with h5py.File(output_file, "w") as f:
        # Create the main dataset
        table = f.create_dataset("flameletTable", data=table_3d)

        # Create axes datasets and attach scales
        dt = h5py.string_dtype(encoding='utf-8')
        f.create_dataset(axes[0], data=np.array(variable_keys, dtype=dt))  # Variables
        f.create_dataset(axes[1], data=Z_means)  # Zmean
        f.create_dataset(axes[2], data=Z_vars)  # Zvar
        f.create_dataset(axes[3], data=cst_values_sorted)  # Cstmean

        # Attach axis labels and scales
        for i, axis in enumerate(axes):
            table.dims[i].label = axis
            f[axis].make_scale(axis)
            table.dims[i].attach_scale(f[axis])

    print(f"HDF5 file successfully saved as '{output_file}'")


if __name__ == "__main__":
    # Path to the input directory containing Excel files
    input_directory = "favre"

    # Generate the HDF5 file
    compile_hdf5(input_directory)
