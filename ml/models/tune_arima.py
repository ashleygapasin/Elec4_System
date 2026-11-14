
import pandas as pd
import numpy as np
import warnings
from itertools import product
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "train.csv")
validation = pd.read_csv(DATA_DIR / "validation.csv")

train_cash = train["cash"]
actual = validation["cash"].to_numpy()

# STEP 1: DEFINE ARIMA PARAMETERS
p_values = [0, 1, 2]
d_values = [0, 1]
q_values = [0, 1, 2]

combinations = list(product(
    p_values,
    d_values,
    q_values
))

results = []

print("TOTAL ARIMA CONFIGURATIONS:", len(combinations))

# STEP 2: TEST EACH CONFIGURATION
for index, order in enumerate(combinations, start=1):

    print(
        f"Testing {index}/{len(combinations)}: "
        f"ARIMA{order}"
    )

    try:
        model = ARIMA(
            train_cash,
            order=order
        )

        fitted = model.fit()

        if not fitted.mle_retvals.get("converged", False):
            print("Skipped: model did not converge")
            continue

        # Forecast all 12 validation months
        forecast = np.asarray(
            fitted.forecast(steps=12)
        )

        if not np.all(np.isfinite(forecast)):
            print("Skipped: invalid forecast")
            continue

        mae = mean_absolute_error(actual, forecast)
        rmse = np.sqrt(mean_squared_error(actual, forecast))
        mape = np.mean(
            np.abs((actual - forecast) / actual)
        ) * 100

        results.append({
            "order": str(order),
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "aic": fitted.aic,
            "bic": fitted.bic
        })

    except Exception as error:
        print("Skipped:", error)

# STEP 3: RANK RESULTS
if not results:
    raise RuntimeError(
        "No ARIMA configurations completed successfully."
    )

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "rmse"
).reset_index(drop=True)

print("\nTOP 5 ARIMA CONFIGURATIONS:")
print(results_df.head(5).to_string(index=False))

# STEP 4: DISPLAY BEST CONFIGURATION
best = results_df.iloc[0]

print("\nBEST ARIMA CONFIGURATION:")
print("Order:", best["order"])
print("MAE:", round(best["mae"], 2))
print("RMSE:", round(best["rmse"], 2))
print("MAPE:", round(best["mape"], 2), "%")

# STEP 5: SAVE RESULTS
OUTPUT_DIR = BASE_DIR / "artifacts" / "model_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

results_df.to_csv(
    OUTPUT_DIR / "arima_tuning_results.csv",
    index=False
)

print("\nARIMA tuning results saved successfully!")
