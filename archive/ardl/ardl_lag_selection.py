
import pandas as pd
from pathlib import Path
from statsmodels.tsa.ardl import ardl_select_order
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.stattools import jarque_bera
from statsmodels.stats.diagnostic import het_breuschpagan
import statsmodels.api as sm

# STEP 1: LOAD DATA
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR / "data" / "processed" / "final_dataset.csv"
)

OUTPUT_DIR = BASE_DIR / "artifacts" / "ardl"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE, parse_dates=["month"])
df = df.sort_values("month").reset_index(drop=True)

y = df["cash"]

X = df[
    ["php_per_usd", "inflation_yoy"]
]

# STEP 2: SELECT ARDL LAGS
# Keep the same maximum lag across candidates
# to make AIC comparisons more consistent.

selection = ardl_select_order(
    endog=y,
    maxlag=3,
    exog=X,
    maxorder=3,
    ic="aic",
    trend="c",
    seasonal=True,
    period=12,
    hold_back=3,
    glob=False
)

print("\nSELECTED ARDL LAGS")
print("AR lags:", selection.ar_lags)
print("Distributed lags:", selection.dl_lags)

# STEP 3: FIT SELECTED MODEL
model = selection.model
results = model.fit()

print("\nSELECTED ARDL MODEL RESULTS")
print(results.summary())

print("\nAIC:", round(results.aic, 2))
print("BIC:", round(results.bic, 2))

# STEP 4: RESIDUAL DIAGNOSTICS
residuals = results.resid

print("\nLJUNG-BOX TEST")
lb = acorr_ljungbox(
    residuals,
    lags=[6, 12],
    return_df=True
)
print(lb)

print("\nJARQUE-BERA NORMALITY TEST")
jb_stat, jb_pvalue, skew, kurtosis = jarque_bera(
    residuals
)
print("Statistic:", round(jb_stat, 4))
print("P-value:", round(jb_pvalue, 4))

print("\nBREUSCH-PAGAN HETEROSKEDASTICITY TEST")
bp = het_breuschpagan(
    residuals,
    sm.add_constant(results.model._x)
)
print("LM Statistic:", round(bp[0], 4))
print("LM P-value:", round(bp[1], 4))

# STEP 5: SAVE SUMMARY
with open(
    OUTPUT_DIR / "selected_ardl_summary.txt",
    "w",
    encoding="utf-8"
) as file:
    file.write(results.summary().as_text())

print("\nARDL lag selection completed!")
