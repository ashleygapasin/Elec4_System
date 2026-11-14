
import pandas as pd
import numpy as np
import warnings
from itertools import product
from pathlib import Path
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "train.csv")
validation = pd.read_csv(DATA_DIR / "validation.csv")

train_cash = train["cash"]
actual = validation["cash"].to_numpy()

# Small initial search to keep runtime manageable
p_values = [0, 1]
d_values = [1]
q_values = [0, 1]

P_values = [0, 1]
D_values = [1]
Q_values = [0, 1]

results = []

combinations = list(product(
    p_values, d_values, q_values,
    P_values, D_values, Q_values
))

print("TOTAL SARIMA CONFIGURATIONS:", len(combinations))

for index, (p, d, q, P, D, Q) in enumerate(combinations, start=1):

    order = (p, d, q)
    seasonal_order = (P, D, Q, 12)

    print(
        f"Testing {index}/{len(combinations)}: "
        f"{order} x {seasonal_order}"
    )

    try:
        model = SARIMAX(
            train_cash,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        fitted = model.fit(disp=False, maxiter=200)

        if not fitted.mle_retvals.get("converged", False):
            print("Skipped: model did not converge")
            continue

        forecast = fitted.forecast(steps=12).to_numpy()

        if not np.all(np.isfinite(forecast)):
            print("Skipped: invalid forecast")
            continue

        mae = mean_absolute_error(actual, forecast)
        rmse = np.sqrt(mean_squared_error(actual, forecast))
        mape = np.mean(np.abs((actual - forecast) / actual)) * 100

        results.append({
            "order": str(order),
            "seasonal_order": str(seasonal_order),
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "aic": fitted.aic,
            "bic": fitted.bic
        })

    except Exception as error:
        print("Skipped:", error)

if not results:
    raise RuntimeError("No SARIMA configurations completed successfully.")

results_df = pd.DataFrame(results)

# Rank models by validation RMSE
results_df = results_df.sort_values(
    "rmse"
).reset_index(drop=True)

print("\nTOP 5 SARIMA CONFIGURATIONS:")
print(results_df.head(5).to_string(index=False))

best = results_df.iloc[0]

print("\nBEST SARIMA CONFIGURATION:")
print("Order:", best["order"])
print("Seasonal Order:", best["seasonal_order"])
print("MAE:", round(best["mae"], 2))
print("RMSE:", round(best["rmse"], 2))
print("MAPE:", round(best["mape"], 2), "%")

OUTPUT_DIR = BASE_DIR / "artifacts" / "model_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

results_df.to_csv(
    OUTPUT_DIR / "sarima_tuning_results.csv",
    index=False
)

print("\nSARIMA tuning results saved successfully!")
