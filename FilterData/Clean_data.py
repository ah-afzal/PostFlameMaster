import os
import shutil

# Define the line numbers (1-based index) to keep (at the beginning)
lines_to_keep = [1, 10, 35, 36, 38]  # Modify this list as needed

# Path to the folder containing the files
source_folder = "FlameMasterOutput"  # Replace with your folder path

destination_folder = "Processed_flamelets"  # New folder for processed files
os.makedirs(destination_folder, exist_ok=True)  # Create the directory if it doesn't exist

# Process each file in the source folder
for filename in os.listdir(source_folder):
    source_file_path = os.path.join(source_folder, filename)
    destination_file_path = os.path.join(destination_folder, filename)

    # Ensure it is a file (skip directories)
    if os.path.isfile(source_file_path):
        # Read the file and filter the lines
        with open(source_file_path, 'r') as file:
            lines = file.readlines()

        # Select only the lines that you want to keep
        filtered_lines = [line for i, line in enumerate(lines, start=1) if i in lines_to_keep]

        # Append the remaining lines after the 38th line
        filtered_lines.extend(lines[38:])  # Keep everything after line 38 intact

        # Remove the last 30 lines from the resulting list
        if len(filtered_lines) > 39:  # Ensure there are at least 39 lines to remove
            filtered_lines = filtered_lines[:-39]

        # Write the filtered content to the new directory
        with open(destination_file_path, 'w') as file:
            file.writelines(filtered_lines)

        print(f"File copied and modified: {destination_file_path}")

print("All files have been processed and copied to the new folder.")
