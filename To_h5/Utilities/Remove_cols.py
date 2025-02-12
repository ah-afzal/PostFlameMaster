# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 19:44:09 2024

@author: afzala
"""

import os
import pandas as pd

# Directory containing Excel files
directory_path = "flamelets"  # Replace with the path to your directory

# Columns to remove (0-based index)
columns_to_remove = list(range(40,78)) # Replace with the indices of columns you want to remove
columns_to_remove.remove(47)
# Process each Excel file in the directory
for file_name in os.listdir(directory_path):
    if file_name.endswith(".xlsx"):  # Only process Excel files
        file_path = os.path.join(directory_path, file_name)
        print(file_path)
        # Load the Excel file
        df = pd.read_excel(file_path)

        # Drop the columns by index
        df = df.drop(df.columns[columns_to_remove], axis=1)

        # Save the modified DataFrame back to the same file
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, index=False)
        
        print(f"Processed file: {file_name}")

print("All files processed!")
