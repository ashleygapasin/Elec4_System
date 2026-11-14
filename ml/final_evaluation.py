
import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# STEP 1: LOAD DATASETS
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "train.csv")
validation = pd.read_csv(DATA_DIR / "validation.csv")
test = pd.read_csv(DATA_DIR / "test.csv")

# Combine training and validation data
development = pd.concat(
    [train, validation],
    ignore_index=True
)

development["month"] = pd.to_datetime(development["month"])
test["month"] = pd.to_datetime(test["month"])

development = development.sort_values("month").reset_index(drop=True)
test = test.sort_values("month").reset_index(drop=True)

assert len(development) == 78
assert len(test) == 12
assert development["month"].max() == pd.Timestamp("2025-06-01")
assert test["month"].min() == pd.Timestamp("2025-07-01")

actual = test["cash"].to_numpy()

# Store all model forecasts
forecasts = {}


# STEP 2: SEASONAL NAIVE
forecasts["Seasonal Naive"] = (
    development["cash"].iloc[-12:].to_numpy().copy()
)

print("Seasonal Naive completed")


# STEP 3: TUNED ARIMA
arima = ARIMA(
    development["cash"],
    order=(0, 1, 0)
)

arima_fit = arima.fit()

forecasts["ARIMA"] = np.asarray(
    arima_fit.forecast(steps=12)
)

print("ARIMA completed")


# STEP 4: TUNED SARIMA
sarima = SARIMAX(
    development["cash"],
    order=(1, 1, 1),
    seasonal_order=(1, 1, 0, 12),
    enforce_stationarity=False,
    enforce_invertibility=False
)

sarima_fit = sarima.fit(disp=False, maxiter=200)

print(
    "SARIMA converged:",
    sarima_fit.mle_retvals.get("converged")
)

if not sarima_fit.mle_retvals.get("converged", False):
    raise RuntimeError("SARIMA did not converge.")

forecasts["SARIMA"] = np.asarray(
    sarima_fit.forecast(steps=12)
)

print("SARIMA completed")


# STEP 5: CREATE XGBOOST TRAINING FEATURES
def create_features(df, include_economic=False):
    df = df.copy()

    df["lag_1"] = df["cash"].shift(1)
    df["lag_2"] = df["cash"].shift(2)
    df["lag_3"] = df["cash"].shift(3)
    df["lag_12"] = df["cash"].shift(12)

    df["month_number"] = pd.to_datetime(
        df["month"]
    ).dt.month

    features = [
        "lag_1", "lag_2", "lag_3",
        "lag_12", "month_number"
    ]

    if include_economic:
        df["exchange_lag_1"] = df["php_per_usd"].shift(1)
        df["inflation_lag_1"] = df["inflation_yoy"].shift(1)

        features += [
            "exchange_lag_1",
            "inflation_lag_1"
        ]

    df = df.dropna(subset=features)

    return df, features


# STEP 6: FUNCTION FOR XGBOOST FORECASTING
def forecast_xgboost(
    n_estimators,
    max_depth,
    learning_rate,
    include_economic=False
):
    training_data, feature_columns = create_features(
        development,
        include_economic
    )

    X_train = training_data[feature_columns]
    y_train = training_data["cash"]

    model = XGBRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        random_state=42,
        objective="reg:squarederror",
        n_jobs=1
    )

    model.fit(X_train, y_train)

    history = development["cash"].tolist()
    predictions = []

    # Last economic values available at June 2025
    last_exchange = float(
        development["php_per_usd"].iloc[-1]
    )

    last_inflation = float(
        development["inflation_yoy"].iloc[-1]
    )

    for month in test["month"]:
        row = {
            "lag_1": history[-1],
            "lag_2": history[-2],
            "lag_3": history[-3],
            "lag_12": history[-12],
            "month_number": month.month
        }

        if include_economic:
            row["exchange_lag_1"] = last_exchange
            row["inflation_lag_1"] = last_inflation

        features = pd.DataFrame(
            [row],
            columns=feature_columns
        )

        prediction = float(
            model.predict(features)[0]
        )

        predictions.append(prediction)
        history.append(prediction)

    return np.array(predictions)


# STEP 7: TUNED XGBOOST A
forecasts["XGBoost A"] = forecast_xgboost(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.1,
    include_economic=False
)

print("XGBoost A completed")


# STEP 8: TUNED XGBOOST B
forecasts["XGBoost B"] = forecast_xgboost(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    include_economic=True
)

print("XGBoost B completed")


# STEP 9: EVALUATE ALL MODELS
comparison = []

forecast_table = pd.DataFrame({
    "month": test["month"],
    "actual": actual
})

for model_name, predicted in forecasts.items():

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    mape = np.mean(
        np.abs((actual - predicted) / actual)
    ) * 100

    comparison.append({
        "model": model_name,
        "mae": mae,
        "rmse": rmse,
        "mape": mape
    })

    forecast_table[model_name] = predicted


# STEP 10: RANK MODELS
comparison_df = pd.DataFrame(comparison)

comparison_df = comparison_df.sort_values(
    "rmse"
).reset_index(drop=True)

print("\nFINAL TESTING RESULTS:")
print(comparison_df.to_string(index=False))

print("\nBEST TEST-PERFORMING MODEL:")
print(comparison_df.iloc[0]["model"])

print("\nACTUAL VS FORECAST:")
print(forecast_table.to_string(index=False))


# STEP 11: SAVE RESULTS
OUTPUT_DIR = BASE_DIR / "artifacts" / "model_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

comparison_df.to_csv(
    OUTPUT_DIR / "final_test_metrics.csv",
    index=False
)

forecast_table.to_csv(
    OUTPUT_DIR / "final_test_forecasts.csv",
    index=False
)

print("\nFinal testing results saved successfully!")
