
import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.statespace.sarimax import SARIMAX

# STEP 1: LOCATE PROJECT FOLDERS
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "final_dataset.csv"

OUTPUT_DIR = BASE_DIR / "artifacts" / "forecasts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# STEP 2: LOAD COMPLETE DATASET
df = pd.read_csv(DATA_FILE, parse_dates=["month"])
df = df.sort_values("month").reset_index(drop=True)

assert len(df) == 90
assert df["month"].max() == pd.Timestamp("2026-06-01")
assert df["cash"].notna().all()

print("TOTAL HISTORICAL MONTHS:", len(df))
print("LAST AVAILABLE MONTH:", df["month"].max())

# STEP 3: TRAIN SELECTED SARIMA MODEL
model = SARIMAX(
    df["cash"],
    order=(1, 1, 1),
    seasonal_order=(1, 1, 0, 12),
    enforce_stationarity=False,
    enforce_invertibility=False
)

fitted_model = model.fit(
    disp=False,
    maxiter=200
)

converged = fitted_model.mle_retvals.get(
    "converged", False
)

print("\nSARIMA CONVERGED:", converged)

if not converged:
    raise RuntimeError("SARIMA did not converge.")

# STEP 4: GENERATE 12-MONTH FORECAST
forecast_result = fitted_model.get_forecast(
    steps=12
)

predictions = np.asarray(
    forecast_result.predicted_mean
)

# 95% prediction intervals
intervals = forecast_result.conf_int(
    alpha=0.05
)

lower_bound = intervals.iloc[:, 0].to_numpy()
upper_bound = intervals.iloc[:, 1].to_numpy()

# STEP 5: CREATE FUTURE MONTHS
last_month = df["month"].max()

future_months = pd.date_range(
    start=last_month + pd.DateOffset(months=1),
    periods=12,
    freq="MS"
)

# STEP 6: ORGANIZE RESULTS
future_df = pd.DataFrame({
    "month": future_months,
    "forecast": predictions,
    "lower_95": lower_bound,
    "upper_95": upper_bound
})

print("\n12-MONTH CASH REMITTANCE FORECAST")
print("Unit: Million USD")
print(future_df.to_string(index=False))

# STEP 7: SAVE FORECAST
future_df.to_csv(
    OUTPUT_DIR / "sarima_future_12_months.csv",
    index=False
)

print("\nFuture forecast saved successfully!")
