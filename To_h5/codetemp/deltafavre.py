import os
import pandas as pd

# Input and output directories
input_folder = 'Modified_Files'
output_folder = 'deltafavre'

# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)




# Columns to exclude from multiplication
include_cols = {'mu', 'ProdRateProgressVariable'}

# Process each CSV file in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        filepath = os.path.join(input_folder, filename)
        df = pd.read_csv(filepath)

        # Perform the multiplication
        for col in df.columns:
            if col in include_cols:
                df[col] = df[col]/df['rho']

        df['rho']=1/df['rho']






        if 'rho' in df.columns and 'mu' in df.columns:
            cols = df.columns.tolist()
            rho_index = cols.index('rho')
            mu_index = cols.index('mu')

            # Swap positions
            cols[rho_index], cols[mu_index] = cols[mu_index], cols[rho_index]
            df = df[cols]



        # Save to new folder with same filename
        output_path = os.path.join(output_folder, filename)
        df.to_csv(output_path, index=False)

print("All files processed and saved in 'deltafavre' folder.")

