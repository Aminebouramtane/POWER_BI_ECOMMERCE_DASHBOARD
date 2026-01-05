import pandas as pd

# Path to your dataset
file_path = "./distribution_centers.csv"

# Load dataset
df = pd.read_csv(file_path)

# Print column names
print("Columns in the dataset:")
for col in df.columns:
    print(col)
