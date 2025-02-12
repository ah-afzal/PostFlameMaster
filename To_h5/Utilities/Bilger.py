import pandas as pd
import re

MOLECULAR_WEIGHTS = {
    "H": 1.008,
    "O": 16.00,
    "N": 14.01,
    "C": 12.01
}

SKIP_SPECIES = ["AR", "HE"]

def parse_species_formula(species: str):
    """Parse the molecular formula and count the number of each element."""
    element_pattern = r"([A-Z][a-z]*)(\d*)"
    element_counts = {}

    matches = re.findall(element_pattern, species)
    for element, count in matches:
        count = int(count) if count else 1
        element_counts[element] = element_counts.get(element, 0) + count

    return element_counts

def calculate_bilger_mixture_fraction(df: pd.DataFrame, start_col: int, end_col: int, yh_o, yh_f, yo_o, yo_f):
    """Calculate Bilger mixture fraction and replace the first column."""
    for index, row in df.iterrows():
        YH = row.iloc[start_col]  # Assuming the hydrogen mass fraction is stored in the first column
        YO = row.iloc[start_col + 1]  # Assuming the oxygen mass fraction is stored in the next column

        # Bilger mixture fraction formula:
        Z = ((YH - yh_o) / (2 * MOLECULAR_WEIGHTS["H"]) - (YO - yo_o) / MOLECULAR_WEIGHTS["O"]) / \
            ((yh_f - yh_o) / (2 * MOLECULAR_WEIGHTS["H"]) - (yo_f - yo_o) / MOLECULAR_WEIGHTS["O"])

        df.loc[index, df.columns[start_col]] = Z  # Replace the first column with Bilger mixture fraction

    return df

# Read the Excel file
input_file = "flamelets/Tst_2113.0_c_st_0.2172681.xlsx"  # Replace with your file path
df = pd.read_excel(input_file)

# Specify the range of columns containing species mass fractions
start_col = 1  # Replace with actual column index for species mass fractions
end_col = 38  # Replace with actual column index for species mass fractions

# Placeholder values for YH,O, YH,F, YO,O, YO,F
yh_o = 0.0
yh_f = 0.057846
yo_o = 0.232882
yo_f = 0.1573

updated_df = calculate_bilger_mixture_fraction(df, start_col, end_col, yh_o, yh_f, yo_o, yo_f)

# Save the updated DataFrame to an Excel file
output_file = "updated_bilger_mixture_fractions.xlsx"
updated_df.to_excel(output_file, index=False)
print("Bilger mixture fraction calculated and saved to updated_bilger_mixture_fractions.xlsx")
