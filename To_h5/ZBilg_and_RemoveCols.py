import os
import pandas as pd
import numpy as np

# ✅ Column names to keep
columns_to_keep = [
    'Z', 'N2', 'H2', 'OH', 'H2O', 'O2', 'OH*', 'NH2', 'NH3', 'NO',
    'lambda', 'mu', 'T', 'rho', 'ProgressVariable', 'ProdRateProgressVariable',
    'D', 'SquareProgVar', 'ProgVarProdRate'
]

# Input and output directories
input_directory = "../Temp/CSV_flamelets"
output_directory = "../Temp/Final_flamelets"
os.makedirs(output_directory, exist_ok=True)

# Process each CSV file
for filename in os.listdir(input_directory):
    if filename.endswith(".csv"):
        file_path = os.path.join(input_directory, filename)
        df = pd.read_csv(file_path)

        if 'ZBilger' in df.columns and 'Z' in df.columns:
            df['Z'] = df['ZBilger']
            df = df.drop(columns=['ZBilger'])

        # ✅ Keep only specified columns
        df = df[[col for col in columns_to_keep if col in df.columns]]
        df = df.apply(pd.to_numeric, downcast='float')

        # Save
        output_file_path = os.path.join(output_directory, filename)
        np.savetxt(output_file_path, df, delimiter=',', fmt='%12.6e', header=','.join(df.columns), comments='')
        print(f"Modified file saved at: {output_file_path}")

print("All files processed and saved in the 'Modified_Files' directory.")
