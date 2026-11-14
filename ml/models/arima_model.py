
import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Locate the project folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

# Load training and validation datasets
train = pd.read_csv(DATA_DIR / "train.csv")
validation = pd.read_csv(DATA_DIR / "validation.csv")

# Get cash remittance values
train_cash = train["cash"]
actual = validation["cash"].to_numpy()

# STEP 1: TRAIN ARIMA MODEL
# ARIMA(p, d, q)
model = ARIMA(
    train_cash,
    order=(1, 1, 1)
)

fitted_model = model.fit()

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
print("ARIMA - VALIDATION RESULTS")
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
    OUTPUT_DIR / "arima_validation.csv",
    index=False
)

print("\nARIMA forecast saved successfully!")
    