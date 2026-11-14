
import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Locate the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

# Load training and validation datasets
train = pd.read_csv(DATA_DIR / "train.csv")
validation = pd.read_csv(DATA_DIR / "validation.csv")

# Get cash remittance values
train_cash = train["cash"]
actual = validation["cash"].to_numpy()

# STEP 1: TRAIN SARIMA MODEL
model = SARIMAX(
    train_cash,
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 12),
    enforce_stationarity=False,
    enforce_invertibility=False
)

fitted_model = model.fit(disp=False)


# STEP 1A: CHECK SARIMA DIAGNOSTICS
print("\nSARIMA MODEL DIAGNOSTICS")

print("Converged:", fitted_model.mle_retvals.get("converged"))

print("AIC:", round(fitted_model.aic, 2))
print("BIC:", round(fitted_model.bic, 2))

# Check model residuals
from statsmodels.stats.diagnostic import acorr_ljungbox

residuals = fitted_model.resid.dropna()

# Remove the first 13 residuals affected by initialization
residuals = residuals.iloc[13:]

ljung_box = acorr_ljungbox(
    residuals,
    lags=[12],
    return_df=True
)

print("\nLJUNG-BOX TEST:")
print(ljung_box)


# STEP 2: FORECAST NEXT 12 MONTHS
forecast = fitted_model.forecast(steps=12).to_numpy()

# STEP 3: EVALUATE FORECASTS
mae = mean_absolute_error(actual, forecast)

rmse = np.sqrt(
    mean_squared_error(actual, forecast)
)

mape = np.mean(
    np.abs((actual - forecast) / actual)
) * 100

# Display metrics
print("SARIMA - VALIDATION RESULTS")
print("MAE:", round(mae, 2))
print("RMSE:", round(rmse, 2))
print("MAPE:", round(mape, 2), "%")

# STEP 4: COMPARE ACTUAL VS FORECAST
results = pd.DataFrame({
    "month": validation["month"],
    "actual": actual,
    "forecast": forecast
})

print("\nACTUAL VS FORECAST:")
print(results.to_string(index=False))

# STEP 5: SAVE FORECAST RESULTS
OUTPUT_DIR = BASE_DIR / "artifacts" / "forecasts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

results.to_csv(
    OUTPUT_DIR / "sarima_validation.csv",
    index=False
)

print("\nSARIMA forecast saved successfully!")
