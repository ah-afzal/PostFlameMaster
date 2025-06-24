import os
import re
import matplotlib.pyplot as plt

directory = "../Temp/Processed_flamelets"  # Replace with directory of flamelets

# Define the threshold for Tst difference
delta = 5.0  # Change this to your desired value (0 for full)

# Initialize lists to store chi and Tst values
chi_values = []
Tst_values = []

# Function to filter Tst values based on the criteria
def filter_tst_values(chi_values, Tst_values, delta):
    # Combine Tst and chi, then sort by Tst
    sorted_data = sorted(zip(Tst_values, chi_values), key=lambda x: x[0])  # Sort by Tst
    filtered_data = [sorted_data[0]]  # Start with the min Tst
    for tst, chi in sorted_data[1:]:
        # Include the point if the difference with the last selected Tst is at least delta
        if abs(tst - filtered_data[-1][0]) >= delta:
            filtered_data.append((tst, chi))
    if filtered_data[-1][0] != sorted_data[-1][0]:  # Ensure max Tst is included
        filtered_data.append(sorted_data[-1])
    # Return chi and Tst separately in the correct order for plotting
    return zip(*filtered_data)

# Loop through all files in the directory
for filename in os.listdir(directory):
    # Extract chi and Tst using regex
    chi_match = re.search(r"chi([\d\.e\+\-]+)", filename)  # Matches chi values
    Tst_match = re.search(r"Tst(\d+)", filename)  # Matches Tst values
    if chi_match and Tst_match:
        chi_values.append(float(chi_match.group(1)))  # Convert chi to float
        Tst_values.append(float(Tst_match.group(1)))  # Convert Tst to float

# Apply the filter function on the extracted data
if chi_values and Tst_values:
    Tst_values, chi_values = filter_tst_values(chi_values, Tst_values, delta)

# Plotting
plt.figure(figsize=(8, 6))
plt.scatter(chi_values, Tst_values, label="Dataset",s=10)  # Correct order for scatter plot
plt.xlabel("Chi (Scalar Dissipation Rate)")
plt.ylabel("Tst (Stagnation Temperature)")
plt.title("Tst vs. Chi (Filtered)")
plt.legend()
plt.grid()
plt.show()
