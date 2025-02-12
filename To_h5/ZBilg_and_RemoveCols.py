

# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 21:36:19 2025

@author: afzala
"""

import os
import pandas as pd
import numpy as np
# Specify the column indices to be removed (1-based index)
columns_to_remove_indices = [n for n in range(40, 58) if n not in {42, 43, 44, 46,48, 57, 58}] 

# Input directory path
input_directory = "flamelets"

# Create an output directory in the current location
output_directory = "Modified_Files"
os.makedirs(output_directory, exist_ok=True)

# Process each Excel file in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith(".csv"):
        file_path = os.path.join(input_directory, filename)

        # Load the Excel file
        df = pd.read_csv(file_path)

        # Skip files if required columns are missing
        if 'ZBilger' in df.columns and 'Z' in df.columns:
            # Replace 'Z' with 'ZBilger' and drop the 'ZBilger' column
            df['Z'] = df['ZBilger']
            df = df.drop(columns=['ZBilger'])

        # Remove columns specified by the 1-based indices
        column_indices_to_remove = [index-2 for index in columns_to_remove_indices if 1 <= index <= len(df.columns)]
        columns_to_remove_names = [df.columns[idx] for idx in column_indices_to_remove]
        df = df.drop(columns=columns_to_remove_names)
        df = df.apply(pd.to_numeric, downcast='float')
        # Save the modified file to the output directory with the same name
        output_file_path = os.path.join(output_directory, filename)
        np.savetxt(output_file_path, df, delimiter=',', fmt='%12.6e', header=','.join(df.columns), comments='')
        print(f"Modified file saved at: {output_file_path}")

print("All files processed and saved in the 'Modified_Files' directory.")
