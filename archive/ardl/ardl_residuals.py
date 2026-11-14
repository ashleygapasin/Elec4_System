
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from statsmodels.tsa.ardl import ardl_select_order
from scipy.stats import skew, kurtosis

# STEP 1: LOAD DATA
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR / "data" / "processed" / "final_dataset.csv"
)

OUTPUT_DIR = BASE_DIR / "artifacts" / "ardl"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE, parse_dates=["month"])
df = df.sort_values("month").reset_index(drop=True)

# STEP 2: REFIT SELECTED ARDL
selection = ardl_select_order(
    endog=df["cash"],
    maxlag=3,
    exog=df[["php_per_usd", "inflation_yoy"]],
    maxorder=3,
    ic="aic",
    trend="c",
    seasonal=True,
    period=12,
    hold_back=3,
    glob=False
)

results = selection.model.fit()

# STEP 3: EXTRACT RESIDUALS
residuals = np.asarray(results.resid)

# Match residuals to estimation months
months = df["month"].iloc[-len(residuals):].reset_index(drop=True)

residual_df = pd.DataFrame({
    "month": months,
    "residual": residuals
})

print("RESIDUAL STATISTICS")
print("Mean:", round(np.mean(residuals), 4))
print("Standard deviation:", round(np.std(residuals), 4))
print("Skewness:", round(skew(residuals), 4))
print("Excess kurtosis:", round(kurtosis(residuals), 4))

# STEP 4: FIND LARGEST RESIDUALS
residual_df["absolute_residual"] = (
    residual_df["residual"].abs()
)

largest = residual_df.nlargest(
    5, "absolute_residual"
)

print("\nTOP 5 LARGEST RESIDUALS")
print(largest.to_string(index=False))

# STEP 5: PLOT RESIDUALS OVER TIME
plt.figure(figsize=(11, 5))
plt.plot(
    residual_df["month"],
    residual_df["residual"]
)
plt.axhline(0, linestyle="--")
plt.title("ARDL Residuals Over Time")
plt.xlabel("Month")
plt.ylabel("Residual (Million USD)")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "ardl_residuals_time.png",
    dpi=150
)
plt.show()

# STEP 6: PLOT RESIDUAL DISTRIBUTION
plt.figure(figsize=(8, 5))
plt.hist(residuals, bins=15, edgecolor="black")
plt.title("ARDL Residual Distribution")
plt.xlabel("Residual (Million USD)")
plt.ylabel("Frequency")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "ardl_residuals_histogram.png",
    dpi=150
)
plt.show()

# STEP 7: SAVE RESIDUALS
residual_df.to_csv(
    OUTPUT_DIR / "ardl_residuals.csv",
    index=False
)

print("\nARDL residual analysis completed!")
