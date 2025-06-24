import os

# Path to the folder containing the files
source_folder = "../Temp/FlameMasterOutput/"
destination_folder = "../Temp/Processed_flamelets"
os.makedirs(destination_folder, exist_ok=True)

# Process each file
for filename in os.listdir(source_folder):
    source_file_path = os.path.join(source_folder, filename)
    destination_file_path = os.path.join(destination_folder, filename)

    if os.path.isfile(source_file_path):
        with open(source_file_path, 'r') as file:
            lines = file.readlines()

        output_lines = []
        body_found = False

        for line in lines:
            stripped = line.strip()

            if stripped == "trailer":
                # 🚫 Stop collecting lines once "trailer" is seen
                break
            elif body_found:
                output_lines.append(line)
            elif stripped == "header":
                output_lines.append(line)
            elif stripped.startswith("Z_st ="):
                output_lines.append(line)
            elif stripped.startswith("numOfSpecies ="):
                output_lines.append(line)
            elif stripped.startswith("gridPoints ="):
                output_lines.append(line)
            elif stripped == "body":
                output_lines.append(line)
                body_found = True

        with open(destination_file_path, 'w') as out_file:
            out_file.writelines(output_lines)

        print(f"Processed: {destination_file_path}")

print("All files have been processed and saved.")
