
import pandas as pd
import warnings
from pathlib import Path
from statsmodels.tsa.stattools import adfuller, kpss

# STEP 1: LOAD DATASET
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR / "data" / "processed" / "final_dataset.csv"
)

df = pd.read_csv(DATA_FILE, parse_dates=["month"])
df = df.sort_values("month").reset_index(drop=True)

inflation = df["inflation_yoy"].dropna()

# STEP 2: DEFINE TEST FUNCTION
def check_stationarity(series, label):

    print("\n" + "=" * 50)
    print(label)
    print("Observations:", len(series))

    # ADF with constant
    adf_c = adfuller(
        series,
        regression="c",
        autolag="AIC",
        result_object=False
    )

    # ADF with constant and trend
    adf_ct = adfuller(
        series,
        regression="ct",
        autolag="AIC",
        result_object=False
    )

    # KPSS with constant
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        kpss_c = kpss(
            series,
            regression="c",
            nlags="auto"
        )

        # KPSS with constant and trend
        kpss_ct = kpss(
            series,
            regression="ct",
            nlags="auto"
        )

    print("\nADF TEST")
    print("Constant p-value:", round(adf_c[1], 4))
    print("Constant + Trend p-value:", round(adf_ct[1], 4))

    print("\nKPSS TEST")
    print("Constant p-value:", round(kpss_c[1], 4))
    print("Constant + Trend p-value:", round(kpss_ct[1], 4))


# STEP 3: TEST INFLATION AT LEVEL
check_stationarity(
    inflation,
    "INFLATION - LEVEL"
)

# STEP 4: TEST FIRST DIFFERENCE
check_stationarity(
    inflation.diff().dropna(),
    "INFLATION - FIRST DIFFERENCE"
)

# STEP 5: TEST SECOND DIFFERENCE
check_stationarity(
    inflation.diff().diff().dropna(),
    "INFLATION - SECOND DIFFERENCE"
)

print("\nInflation verification completed!")
