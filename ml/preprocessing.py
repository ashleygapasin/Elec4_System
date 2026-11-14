
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "2019-01-01"
END_DATE = "2026-06-01"


# STEP 1: LOAD CASH REMITTANCES
remit_file = next(RAW_DIR.glob("Original_ofwp*.xlsx"))

remit = pd.read_excel(
    remit_file,
    sheet_name="monthly 1970-June2026",
    header=None
)

remit = remit[[1, 4, 6]].copy()
remit.columns = ["year", "month", "cash"]


# Read the original year labels
remit["year"] = remit["year"].astype("string")

# Detect preliminary years
remit["preliminary"] = remit["year"].str.contains(
    "p", case=False, na=False
)

# Carry preliminary status to monthly rows
remit["preliminary"] = (
    remit["preliminary"]
    .where(remit["year"].notna())
    .ffill()
    .fillna(False)
    .astype(bool)
)

# Extract and fill the year
remit["year"] = (
    remit["year"]
    .str.extract(r"(\d{4})")[0]
    .ffill()
)


# Keep valid month rows
remit["month"] = remit["month"].astype("string").str.strip()

remit = remit[
    remit["month"].isin([
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ])
].copy()

remit["date"] = pd.to_datetime(
    remit["year"] + "-" + remit["month"],
    format="%Y-%B"
)

remit["cash"] = pd.to_numeric(remit["cash"], errors="coerce")

remit = remit[
    (remit["date"] >= START_DATE) &
    (remit["date"] <= END_DATE)
]

remit = remit[["date", "cash", "preliminary"]]


# STEP 2: LOAD EXCHANGE RATES
exchange_file = next(RAW_DIR.glob("Original_ExchangeRate*.xlsx"))

exchange = pd.read_excel(
    exchange_file,
    sheet_name="monthly",
    header=None
)

exchange = exchange[[1, 2, 3]].copy()
exchange.columns = ["year", "month", "php_per_usd"]

exchange["year"] = (
    exchange["year"]
    .astype("string")
    .str.extract(r"(\d{4})")[0]
    .ffill()
)

exchange["month"] = exchange["month"].astype("string").str.strip()

exchange = exchange[
    exchange["month"].isin([
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ])
].copy()

exchange["date"] = pd.to_datetime(
    exchange["year"] + "-" + exchange["month"],
    format="%Y-%B"
)

exchange["php_per_usd"] = pd.to_numeric(
    exchange["php_per_usd"],
    errors="coerce"
)

exchange = exchange[
    (exchange["date"] >= START_DATE) &
    (exchange["date"] <= END_DATE)
]

exchange = exchange[["date", "php_per_usd"]]


# STEP 3: MERGE THE TWO DATASETS
merged = pd.merge(
    remit,
    exchange,
    on="date",
    how="inner"
)

merged = merged.sort_values("date").reset_index(drop=True)

print("\nMERGED DATASET:")
print(merged.head(5))

print("\nLAST 5 ROWS:")
print(merged.tail(5))

print("\nTOTAL MONTHS:", len(merged))
print("\nMISSING VALUES:")
print(merged.isnull().sum())

# Save temporary merged dataset
output_file = PROCESSED_DIR / "remittance_exchange_merged.csv"
merged.to_csv(output_file, index=False)

print("\nSaved to:", output_file)


# STEP 4: LOAD AND CLEAN CPI DATASET

cpi_file = RAW_DIR / "2M4ACP22.xlsx"

cpi_raw = pd.read_excel(
    cpi_file,
    sheet_name="2M4ACP22",
    header=None
)

# The CPI dataset stores years and months horizontally
# Row 2 contains years
# Row 3 contains months
# Row 4 contains the Philippines All Items CPI values

years = cpi_raw.iloc[2, 2:].ffill()
months = cpi_raw.iloc[3, 2:]
values = cpi_raw.iloc[4, 2:]

cpi = pd.DataFrame({
    "year": years.values,
    "month": months.values,
    "cpi": values.values
})

# Convert the year and CPI values into numbers
cpi["year"] = pd.to_numeric(cpi["year"], errors="coerce")
cpi["cpi"] = pd.to_numeric(cpi["cpi"], errors="coerce")

# Create a monthly date
cpi["date"] = pd.to_datetime(
    cpi["year"].astype("Int64").astype(str)
    + "-" + cpi["month"].astype(str),
    format="%Y-%b",
    errors="coerce"
)

# Remove invalid rows
cpi = cpi.dropna(subset=["date", "cpi"])

# Sort chronologically
cpi = cpi.sort_values("date").reset_index(drop=True)

# Calculate year-on-year inflation
# 2018 values are needed to calculate 2019 inflation
cpi["inflation_yoy"] = cpi["cpi"].pct_change(
    periods=12,
    fill_method=None
) * 100

# Keep January 2019 to June 2026
cpi = cpi[
    (cpi["date"] >= START_DATE) &
    (cpi["date"] <= END_DATE)
]

cpi = cpi[["date", "cpi", "inflation_yoy"]]

print("\nCPI DATASET:")
print(cpi.head())

print("\nLAST 5 CPI ROWS:")
print(cpi.tail())

print("\nTOTAL CPI MONTHS:", len(cpi))

print("\nMISSING VALUES:")
print(cpi.isnull().sum())


# STEP 5: MERGE ALL THREE DATASETS

final = pd.merge(
    merged,
    cpi,
    on="date",
    how="inner"
)

final = final.sort_values("date").reset_index(drop=True)

# Calculate year-on-year percentage changes
final["cash_yoy"] = final["cash"].pct_change(
    periods=12,
    fill_method=None
) * 100

final["php_per_usd_yoy"] = final["php_per_usd"].pct_change(
    periods=12,
    fill_method=None
) * 100

# Rename date column
final = final.rename(columns={"date": "month"})

# Arrange columns
final = final[
    [
        "month",
        "cash",
        "cash_yoy",
        "php_per_usd",
        "php_per_usd_yoy",
        "cpi",
        "inflation_yoy",
        "preliminary"
    ]
]

# Check the final dataset
print("\nFINAL DATASET:")
print(final.head(15))

print("\nLAST 5 ROWS:")
print(final.tail())

print("\nTOTAL MONTHS:", len(final))

print("\nMISSING VALUES:")
print(final.isnull().sum())

# Save final dataset
output_file = PROCESSED_DIR / "final_dataset.csv"
final.to_csv(output_file, index=False)

print("\nFinal dataset saved to:", output_file)
