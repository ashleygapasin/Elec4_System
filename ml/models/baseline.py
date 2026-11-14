
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Locate the project folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

# Load training and validation data
train = pd.read_csv(DATA_DIR / "train.csv")
validation = pd.read_csv(DATA_DIR / "validation.csv")

# Get actual remittance values
train_cash = train["cash"].to_numpy()
actual = validation["cash"].to_numpy()

# Seasonal Naive: repeat the last 12 training months
forecast = train_cash[-12:].copy()

# Calculate evaluation metrics
mae = mean_absolute_error(actual, forecast)
rmse = np.sqrt(mean_squared_error(actual, forecast))
mape = np.mean(np.abs((actual - forecast) / actual)) * 100

# Display results
print("SEASONAL NAIVE - VALIDATION RESULTS")
print("MAE:", round(mae, 2))
print("RMSE:", round(rmse, 2))
print("MAPE:", round(mape, 2), "%")

# Compare actual and predicted values
results = pd.DataFrame({
    "month": validation["month"],
    "actual": actual,
    "forecast": forecast
})

print("\nACTUAL VS FORECAST:")
print(results.to_string(index=False))

# Save forecasts
OUTPUT_DIR = BASE_DIR / "artifacts" / "forecasts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

results.to_csv(
    OUTPUT_DIR / "seasonal_naive_validation.csv",
    index=False
)

print("\nForecast saved successfully!")
