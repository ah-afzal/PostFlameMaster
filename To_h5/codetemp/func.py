import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from matplotlib.path import Path

# Load CSV file
df = pd.read_csv("compiled_output.csv")  # Change this to your actual filename

# Extract independent variables (Z and c)
Z = df['Z'].values
c = df['H2O'].values

# Find maximum value of c from the data
max_c = np.max(c)
print(max_c)

# Extract dependent variables (all except Z and c)
dependent_vars = [col for col in df.columns if col not in ['Z', 'H2O']]

# Define structured grid (100 x 100 points)
num_points = 100
Z_grid = np.linspace(0, 1, num_points)  # Structured Z values (still between 0 and 1)
c_grid = np.linspace(0, max_c, num_points)  # Structured c values (between 0 and max_c)

# Create meshgrid with 'ij' indexing
Z_mesh, c_mesh = np.meshgrid(Z_grid, c_grid, indexing='ij')

# Flatten grid points for easier processing
grid_points = np.vstack((Z_mesh.ravel(), c_mesh.ravel())).T

# Check if points are inside the convex hull using inpolygon approach
hull_path = Path(np.vstack((Z, c)).T)  # Create a polygon from data points
inside_hull = hull_path.contains_points(grid_points).reshape(Z_mesh.shape)

# Dictionary to store interpolated functions
f = {}

# Interpolate each dependent variable
for var in dependent_vars:
    values = df[var].values  # Function values from the dataset
    
    # Cubic interpolation
    cubic_interp = griddata((Z, c), values, (Z_mesh, c_mesh), method='cubic')
    
    # Nearest interpolation (fallback)
    nearest_interp = griddata((Z, c), values, (Z_mesh, c_mesh), method='nearest')
    
    # Use cubic where valid, otherwise nearest
    interpolated_values = np.where(inside_hull, cubic_interp, nearest_interp)
    
    # Store in dictionary
    f[var] = interpolated_values

# Example: Accessing the interpolated value for a specific Z and c index
z_index, c_index = 43, 0  # Example indices
print(f"Interpolated value at Z[{z_index}], c[{c_index}]: {f['T'][z_index, c_index]}")

