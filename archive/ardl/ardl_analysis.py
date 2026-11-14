
import pandas as pd
from pathlib import Path
from statsmodels.tsa.ardl import ARDL

# STEP 1: LOCATE DATASET
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "final_dataset.csv"

OUTPUT_DIR = BASE_DIR / "artifacts" / "ardl"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# STEP 2: LOAD DATA
df = pd.read_csv(DATA_FILE, parse_dates=["month"])
df = df.sort_values("month").reset_index(drop=True)

# STEP 3: SELECT VARIABLES
# cash = dependent variable
# php_per_usd and inflation_yoy = explanatory variables

variables = df[
    ["cash", "php_per_usd", "inflation_yoy"]
].copy()

print("ARDL DATASET INFORMATION")
print("Observations:", len(variables))
print("\nMissing values:")
print(variables.isna().sum())

# STEP 4: FIT INITIAL ARDL MODEL
# 1 lag for cash
# 1 lag for each economic indicator

model = ARDL(
    endog=variables["cash"],
    lags=1,
    exog=variables[["php_per_usd", "inflation_yoy"]],
    order=1,
    trend="c",
    causal=False
)

results = model.fit()

# STEP 5: DISPLAY RESULTS
print("\nARDL MODEL RESULTS")
print(results.summary())

print("\nMODEL INFORMATION")
print("AIC:", round(results.aic, 2))
print("BIC:", round(results.bic, 2))

# STEP 6: SAVE SUMMARY
summary_file = OUTPUT_DIR / "ardl_summary.txt"

with open(summary_file, "w", encoding="utf-8") as file:
    file.write(results.summary().as_text())

print("\nARDL summary saved successfully!")
