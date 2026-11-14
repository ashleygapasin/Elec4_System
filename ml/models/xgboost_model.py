
import pandas as pd
import numpy as np
from pathlib import Path
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "train.csv")
validation = pd.read_csv(DATA_DIR / "validation.csv")

# STEP 1: CREATE LAG FEATURES
def create_features(df):
    df = df.copy()

    df["lag_1"] = df["cash"].shift(1)
    df["lag_2"] = df["cash"].shift(2)
    df["lag_3"] = df["cash"].shift(3)
    df["lag_12"] = df["cash"].shift(12)

    df["month_number"] = pd.to_datetime(
        df["month"]
    ).dt.month

    return df.dropna(subset=[
        "lag_1", "lag_2", "lag_3", "lag_12"
    ])


train_features = create_features(train)

feature_columns = [
    "lag_1",
    "lag_2",
    "lag_3",
    "lag_12",
    "month_number"
]

X_train = train_features[feature_columns]
y_train = train_features["cash"]

# STEP 2: TRAIN XGBOOST
model = XGBRegressor(
    n_estimators=200,
    max_depth=3,
    learning_rate=0.05,
    random_state=42,
    objective="reg:squarederror"
)

model.fit(X_train, y_train)

# STEP 3: RECURSIVE 12-MONTH FORECAST
history = train["cash"].tolist()
forecast = []

future_months = pd.to_datetime(validation["month"])

for month in future_months:
    features = pd.DataFrame([{
        "lag_1": history[-1],
        "lag_2": history[-2],
        "lag_3": history[-3],
        "lag_12": history[-12],
        "month_number": month.month
    }])

    prediction = float(model.predict(features)[0])

    forecast.append(prediction)

    # Use prediction for the next forecasting step
    history.append(prediction)

# STEP 4: EVALUATE
actual = validation["cash"].to_numpy()
forecast = np.array(forecast)

mae = mean_absolute_error(actual, forecast)
rmse = np.sqrt(mean_squared_error(actual, forecast))
mape = np.mean(np.abs((actual - forecast) / actual)) * 100

print("XGBOOST A - VALIDATION RESULTS")
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
    OUTPUT_DIR / "xgboost_a_validation.csv",
    index=False
)

print("\nXGBoost A forecast saved successfully!")
