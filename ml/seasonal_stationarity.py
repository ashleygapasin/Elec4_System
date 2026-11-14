
import pandas as pd
import numpy as np
from pathlib import Path
import statsmodels.api as sm

# STEP 1: LOAD DATA
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR / "data" / "processed" / "final_dataset.csv"
)

df = pd.read_csv(DATA_FILE, parse_dates=["month"])
df = df.sort_values("month").reset_index(drop=True)

# STEP 2: CREATE MONTH DUMMIES
month_dummies = pd.get_dummies(
    df["month"].dt.month,
    prefix="month",
    drop_first=True,
    dtype=float
)

# STEP 3: ADF-STYLE REGRESSION WITH SEASONAL CONTROLS
def seasonal_adf(series, label, lag_count=12):

    data = pd.DataFrame({
        "y": series.astype(float)
    })

    data["delta_y"] = data["y"].diff()
    data["lag_y"] = data["y"].shift(1)

    for lag in range(1, lag_count + 1):
        data[f"delta_lag_{lag}"] = (
            data["delta_y"].shift(lag)
        )

    data = pd.concat(
        [data, month_dummies],
        axis=1
    ).dropna()

    y = data["delta_y"]

    feature_columns = [
        "lag_y"
    ] + [
        f"delta_lag_{lag}"
        for lag in range(1, lag_count + 1)
    ] + list(month_dummies.columns)

    X = sm.add_constant(
        data[feature_columns]
    )

    result = sm.OLS(y, X).fit()

    print("\n" + "=" * 50)
    print(label)
    print("Observations:", len(data))
    print("Lagged level coefficient:", round(result.params["lag_y"], 4))
    print("Lagged level t-statistic:", round(result.tvalues["lag_y"], 4))
    print("R-squared:", round(result.rsquared, 4))

    print(
        "\nNote: Do not interpret the ordinary OLS "
        "p-value for lag_y as a standard ADF p-value."
    )


# STEP 4: RUN TESTS
inflation = df["inflation_yoy"]

seasonal_adf(
    inflation,
    "INFLATION LEVEL WITH SEASONAL CONTROLS"
)

seasonal_adf(
    inflation.diff(),
    "INFLATION FIRST DIFFERENCE WITH SEASONAL CONTROLS"
)

print("\nSeasonal stationarity diagnostics completed!")
