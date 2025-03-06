import os
import pandas as pd

def compile_csv_files(directory, output_file):
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the directory.")
        return
    
    compiled_data = []
    
    for idx, file in enumerate(csv_files):
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path)
        
        if idx == 0:
            compiled_data.append(df)  # Keep header
        else:
            compiled_data.append(df.iloc[1:])  # Remove top row
    
    final_df = pd.concat(compiled_data, ignore_index=True)
    final_df.to_csv(output_file, index=False)
    print(f"Compiled CSV saved as {output_file}")

# Example usage
directory = "Modified_Files"  # Change this to your directory path
output_file = "compiled_output.csv"  # Output file name
compile_csv_files(directory, output_file)

