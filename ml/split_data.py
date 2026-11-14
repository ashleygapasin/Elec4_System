
import pandas as pd
from pathlib import Path

# Locate project folders
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "final_dataset.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

# Load the dataset
df = pd.read_csv(DATA_FILE, parse_dates=["month"])

# Arrange data chronologically
df = df.sort_values("month").reset_index(drop=True)

# Split the dataset by date
train = df[df["month"] <= "2024-06-01"].copy()

validation = df[
    (df["month"] >= "2024-07-01") &
    (df["month"] <= "2025-06-01")
].copy()

test = df[
    (df["month"] >= "2025-07-01") &
    (df["month"] <= "2026-06-01")
].copy()

# Verify the expected sizes
assert len(train) == 66, "Training data should contain 66 months"
assert len(validation) == 12, "Validation data should contain 12 months"
assert len(test) == 12, "Testing data should contain 12 months"

# Save each dataset
train.to_csv(OUTPUT_DIR / "train.csv", index=False)
validation.to_csv(OUTPUT_DIR / "validation.csv", index=False)
test.to_csv(OUTPUT_DIR / "test.csv", index=False)

# Display results
print("DATA SPLIT COMPLETED")

print("\nTRAINING DATA:")
print(train["month"].min(), "to", train["month"].max())
print("Observations:", len(train))

print("\nVALIDATION DATA:")
print(validation["month"].min(), "to", validation["month"].max())
print("Observations:", len(validation))

print("\nTESTING DATA:")
print(test["month"].min(), "to", test["month"].max())
print("Observations:", len(test))
