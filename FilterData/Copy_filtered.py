import os
import re
import shutil
import matplotlib.pyplot as plt

# Define directories for dataset
directory = "Processed_flamelets"  # Replace with the source directory
filtered_folder = "Filtered_flamelets"  # Replace with the output directory
os.makedirs(filtered_folder, exist_ok=True)  # Create the folder if it doesn't exist

# Define the threshold for `Tst` difference
delta = 10.0  # Change this to your desired value

# Initialize lists to store chi and Tst values
chi_values = []
Tst_values = []
file_map = {}

# Loop through all files in the directory
for filename in os.listdir(directory):
    # Extract chi and Tst using regex
    chi_match = re.search(r"chi([\d\.e\+\-]+)", filename)  # Matches chi values
    Tst_match = re.search(r"Tst(\d+)", filename)  # Matches Tst values
    
    if chi_match and Tst_match:
        chi = float(chi_match.group(1))  # Convert chi to float
        Tst = float(Tst_match.group(1))  # Convert Tst to float
        
        chi_values.append(chi)
        Tst_values.append(Tst)
        file_map[(chi, Tst)] = filename

# Function to filter Tst values based on the criteria
def filter_tst_values(chi_values, Tst_values, delta):
    sorted_data = sorted(zip(Tst_values, chi_values), key=lambda x: x[0])  # Sort by Tst
    filtered_data = [sorted_data[0]]  # Start with the min Tst
    
    for tst, chi in sorted_data[1:]:
        if abs(tst - filtered_data[-1][0]) >= delta:  # Ensure difference meets delta
            filtered_data.append((tst, chi))
    
    if filtered_data[-1][0] != sorted_data[-1][0]:  # Ensure max Tst is included
        filtered_data.append(sorted_data[-1])
    
    return zip(*filtered_data)  # Return chi and Tst separately

# Apply delta filtering
if chi_values and Tst_values:
    Tst_values, chi_values = filter_tst_values(chi_values, Tst_values, delta)

# Copy filtered files to the new folder
for chi, Tst in zip(chi_values, Tst_values):
    filename = file_map.get((chi, Tst))
    if filename:
        src_path = os.path.join(directory, filename)
        dest_path = os.path.join(filtered_folder, filename)
        shutil.copy(src_path, dest_path)
        print(f"File copied: {filename}")

# Plotting
plt.figure(figsize=(8, 6))
plt.scatter(chi_values, Tst_values, label="Filtered Data")
plt.xlabel("Chi (Scalar Dissipation Rate)")
plt.ylabel("Tst (Stagnation Temperature)")
plt.title("Tst vs. Chi (Filtered)")
plt.legend()
plt.grid()
plt.show()

print(f"Filtered files have been copied to: {filtered_folder}")