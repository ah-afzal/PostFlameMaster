# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 19:44:09 2024

@author: afzala
"""

import os
import pandas as pd

# Directory containing Excel files
directory_path = "../Modified_Files"  # Replace with the path to your directory



# Indices you want to keep..1based Index
#columns_to_keep =[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
columns_to_keep =[1,3,5,8,9,12,13,16,17,23,40,42,46,47,48,49,50,51,52]
#columns_to_keep =[1,3,5,8,9,12,13,16,17,23,40,42,43,44,45,46,47,48,49,50,51,52,53]  # Modify this list with the indices you want



#columns_to_keep =[1,2,3,4,5,6,7,8,9,13,30,32,36,37,38,39,40]
#columns_to_keep =[1,3,5,8,9,12,13,16,17,23,40,42,46,47,48,49,50]  # Modify this list with the indices you want








columns_to_keep_0based=[x-1 for x in columns_to_keep]
# Generate the list of indices to remove
columns_to_remove= [i for i in range(0, 52) if i not in columns_to_keep_0based]
#columns_to_remove= [i for i in range(0, 52) if i not in columns_to_keep_0based]
print(columns_to_remove)

# Columns to remove (0-based index)
#columns_to_remove = list(range(40,78)) # Replace with the indices of columns you want to remove
#columns_to_remove.remove(47)
# Process each Excel file in the directory
for file_name in os.listdir(directory_path):
    if file_name.endswith(".csv"):  # Only process Excel files
        file_path = os.path.join(directory_path, file_name)
        print(file_path)
        # Load the Excel file
        df = pd.read_csv(file_path)

        # Drop the columns by index
        df = df.drop(df.columns[columns_to_remove], axis=1)

        # Save the modified DataFrame back to the same file
        df.to_csv(file_path, index=False)
        print(f"Processed file: {file_name}")

print("All files processed!")
