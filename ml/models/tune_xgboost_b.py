
import pandas as pd
import numpy as np
from pathlib import Path
from itertools import product
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "train.csv")
validation = pd.read_csv(DATA_DIR / "validation.csv")

# STEP 1: CREATE TRAINING FEATURES
def create_features(df):
    df = df.copy()

    df["lag_1"] = df["cash"].shift(1)
    df["lag_2"] = df["cash"].shift(2)
    df["lag_3"] = df["cash"].shift(3)
    df["lag_12"] = df["cash"].shift(12)

    df["exchange_lag_1"] = df["php_per_usd"].shift(1)
    df["inflation_lag_1"] = df["inflation_yoy"].shift(1)

    df["month_number"] = pd.to_datetime(
        df["month"]
    ).dt.month

    required_columns = [
        "lag_1", "lag_2", "lag_3", "lag_12",
        "exchange_lag_1", "inflation_lag_1"
    ]

    return df.dropna(subset=required_columns)


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

actual = validation["cash"].to_numpy()
future_months = pd.to_datetime(validation["month"])

# Last available economic indicators at forecast origin
last_exchange = float(train["php_per_usd"].iloc[-1])
last_inflation = float(train["inflation_yoy"].iloc[-1])

# STEP 2: DEFINE HYPERPARAMETERS
n_estimators_values = [100, 200, 300]
max_depth_values = [2, 3, 4]
learning_rate_values = [0.03, 0.05, 0.1]

combinations = list(product(
    n_estimators_values,
    max_depth_values,
    learning_rate_values
))

results = []

print("TOTAL XGBOOST B CONFIGURATIONS:", len(combinations))

# STEP 3: TEST EACH CONFIGURATION
for index, (n_estimators, max_depth, learning_rate) in enumerate(
    combinations, start=1
):

    print(
        f"Testing {index}/{len(combinations)}: "
        f"n_estimators={n_estimators}, "
        f"max_depth={max_depth}, "
        f"learning_rate={learning_rate}"
    )

    model = XGBRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        random_state=42,
        objective="reg:squarederror",
        n_jobs=1
    )

    model.fit(X_train, y_train)

    # STEP 4: RECURSIVE 12-MONTH FORECAST
    history = train["cash"].tolist()
    forecast = []

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
        history.append(prediction)

    forecast = np.array(forecast)

    # STEP 5: CALCULATE METRICS
    mae = mean_absolute_error(actual, forecast)
    rmse = np.sqrt(mean_squared_error(actual, forecast))
    mape = np.mean(
        np.abs((actual - forecast) / actual)
    ) * 100

    results.append({
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "learning_rate": learning_rate,
        "mae": mae,
        "rmse": rmse,
        "mape": mape
    })

# STEP 6: RANK CONFIGURATIONS
results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "rmse"
).reset_index(drop=True)

print("\nTOP 5 XGBOOST B CONFIGURATIONS:")
print(results_df.head(5).to_string(index=False))

best = results_df.iloc[0]

print("\nBEST XGBOOST B CONFIGURATION:")
print("n_estimators:", int(best["n_estimators"]))
print("max_depth:", int(best["max_depth"]))
print("learning_rate:", best["learning_rate"])
print("MAE:", round(best["mae"], 2))
print("RMSE:", round(best["rmse"], 2))
print("MAPE:", round(best["mape"], 2), "%")

# STEP 7: SAVE RESULTS
OUTPUT_DIR = BASE_DIR / "artifacts" / "model_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

results_df.to_csv(
    OUTPUT_DIR / "xgboost_b_tuning_results.csv",
    index=False
)

print("\nXGBoost B tuning results saved successfully!")
