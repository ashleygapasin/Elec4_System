
import pandas as pd
import numpy as np
from pathlib import Path
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Locate project folders
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

# Load datasets
train = pd.read_csv(DATA_DIR / "train.csv")
validation = pd.read_csv(DATA_DIR / "validation.csv")

# STEP 1: CREATE FEATURES
def create_features(df):
    df = df.copy()

    # Historical remittance values
    df["lag_1"] = df["cash"].shift(1)
    df["lag_2"] = df["cash"].shift(2)
    df["lag_3"] = df["cash"].shift(3)
    df["lag_12"] = df["cash"].shift(12)

    # Previous month's economic indicators
    df["exchange_lag_1"] = df["php_per_usd"].shift(1)
    df["inflation_lag_1"] = df["inflation_yoy"].shift(1)

    # Month number
    df["month_number"] = pd.to_datetime(
        df["month"]
    ).dt.month

    return df.dropna(subset=[
        "lag_1", "lag_2", "lag_3", "lag_12",
        "exchange_lag_1", "inflation_lag_1"
    ])


train_features = create_features(train)

feature_columns = [
    "lag_1",
    "lag_2",
    "lag_3",
    "lag_12",
    "exchange_lag_1",
    "inflation_lag_1",
    "month_number"
]

X_train = train_features[feature_columns]
y_train = train_features["cash"]

# STEP 2: TRAIN XGBOOST B
model = XGBRegressor(
    n_estimators=200,
    max_depth=3,
    learning_rate=0.05,
    random_state=42,
    objective="reg:squarederror"
)

model.fit(X_train, y_train)

# STEP 3: PREPARE 12-MONTH FORECAST
history = train["cash"].tolist()
forecast = []

# Last known economic values at June 2024
last_exchange = float(train["php_per_usd"].iloc[-1])
last_inflation = float(train["inflation_yoy"].iloc[-1])

future_months = pd.to_datetime(validation["month"])

for month in future_months:

    features = pd.DataFrame([{
        "lag_1": history[-1],
        "lag_2": history[-2],
        "lag_3": history[-3],
        "lag_12": history[-12],
        "exchange_lag_1": last_exchange,
        "inflation_lag_1": last_inflation,
        "month_number": month.month
    }])

    prediction = float(model.predict(features)[0])

    forecast.append(prediction)

    # Use forecast values for subsequent months
    history.append(prediction)

# STEP 4: EVALUATE
actual = validation["cash"].to_numpy()
forecast = np.array(forecast)

mae = mean_absolute_error(actual, forecast)
rmse = np.sqrt(mean_squared_error(actual, forecast))
mape = np.mean(np.abs((actual - forecast) / actual)) * 100

print("XGBOOST B - VALIDATION RESULTS")
print("MAE:", round(mae, 2))
print("RMSE:", round(rmse, 2))
print("MAPE:", round(mape, 2), "%")

# STEP 5: SAVE RESULTS
results = pd.DataFrame({
    "month": validation["month"],
    "actual": actual,
    "forecast": forecast
})

print("\nACTUAL VS FORECAST:")
print(results.to_string(index=False))

OUTPUT_DIR = BASE_DIR / "artifacts" / "forecasts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

results.to_csv(
    OUTPUT_DIR / "xgboost_b_validation.csv",
    index=False
)

print("\nXGBoost B forecast saved successfully!")
