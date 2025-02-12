import os
import re
import matplotlib.pyplot as plt

# Path to the folder containing the files
folder_path = "flamelets"

# Regex pattern to match Tst and c_st values regardless of digit count
pattern = r"Tst_([+-]?\d*\.?\d+([eE][+-]?\d+)?)+_c_st_([+-]?\d*\.?\d+([eE][+-]?\d+)?)"

# Lists to store the extracted values
Tst_values = []
c_st_values = []

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    match = re.search(pattern, filename)
    if match:
        # Extract the Tst and c_st values
        Tst_values.append(float(match.group(1)))
        c_st_values.append(float(match.group(3)))

# Sort values based on c_st to avoid disjointed lines
sorted_data = sorted(zip(c_st_values, Tst_values))
c_st_values, Tst_values = zip(*sorted_data)

# Plot with sorted data
plt.figure(figsize=(8, 6))
plt.scatter(c_st_values, Tst_values, marker='o', linestyle='-', color='b')
plt.xlabel('c_st')
plt.ylabel('Tst')
plt.title('Tst vs c_st Plot (Ordered)')
plt.grid(True)
plt.show()
