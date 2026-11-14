
import pandas as pd
from pathlib import Path
from statsmodels.tsa.ardl import ardl_select_order
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.stattools import jarque_bera

# STEP 1: PROJECT PATHS
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR / "data" / "processed" / "final_dataset.csv"
)

OUTPUT_DIR = BASE_DIR / "artifacts" / "ardl"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# STEP 2: LOAD DATA
df = pd.read_csv(DATA_FILE, parse_dates=["month"])
df = df.sort_values("month").reset_index(drop=True)

# STEP 3: SELECT AND FIT ARDL MODEL
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

# STEP 4: EXPORT COEFFICIENTS
coefficients = pd.DataFrame({
    "variable": results.params.index,
    "coefficient": results.params.values,
    "p_value": results.pvalues.values
})

coefficients["significant_5pct"] = (
    coefficients["p_value"] < 0.05
)

coefficients.to_csv(
    OUTPUT_DIR / "ardl_coefficients.csv",
    index=False
)

# STEP 5: EXPORT DIAGNOSTICS
lb = acorr_ljungbox(
    results.resid,
    lags=[6, 12],
    return_df=True
)

jb = jarque_bera(results.resid)

diagnostics = pd.DataFrame([
    {
        "test": "Ljung-Box lag 6",
        "p_value": lb.loc[6, "lb_pvalue"]
    },
    {
        "test": "Ljung-Box lag 12",
        "p_value": lb.loc[12, "lb_pvalue"]
    },
    {
        "test": "Jarque-Bera",
        "p_value": jb[1]
    }
])

diagnostics.to_csv(
    OUTPUT_DIR / "ardl_diagnostics.csv",
    index=False
)

# STEP 6: DISPLAY RESULTS
print("\nARDL COEFFICIENTS")
print(coefficients.to_string(index=False))

print("\nARDL DIAGNOSTICS")
print(diagnostics.to_string(index=False))

print("\nARDL dashboard files saved successfully!")
