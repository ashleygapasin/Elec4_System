
import pandas as pd
from pathlib import Path
from statsmodels.tsa.stattools import adfuller

# STEP 1: LOAD DATA
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR / "data" / "processed" / "final_dataset.csv"
)

df = pd.read_csv(DATA_FILE, parse_dates=["month"])
df = df.sort_values("month").reset_index(drop=True)

variables = [
    "cash",
    "php_per_usd",
    "inflation_yoy"
]

# STEP 2: FUNCTION FOR ADF TEST
def run_adf(series, variable_name, stage):

    series = series.dropna()

    result = adfuller(
    series,
    autolag="AIC",
    regression="c",
    result_object=False
)
    p_value = result[1]

    print(f"\nVARIABLE: {variable_name}")
    print("Stage:", stage)
    print("ADF Statistic:", round(result[0], 4))
    print("P-value:", round(p_value, 4))
    print("Lags Used:", result[2])

    if p_value < 0.05:
        print("Result: Reject unit root null hypothesis")
    else:
        print("Result: Cannot reject unit root null hypothesis")

    return p_value


# STEP 3: TEST LEVEL AND DIFFERENCES
for variable in variables:

    print("\n" + "=" * 45)

    # Original values
    level_p = run_adf(
        df[variable],
        variable,
        "Level"
    )

    # First difference
    first_diff = df[variable].diff()

    diff_p = run_adf(
        first_diff,
        variable,
        "First Difference"
    )

    # Second difference (diagnostic only)
    second_diff = first_diff.diff()

    second_p = run_adf(
        second_diff,
        variable,
        "Second Difference"
    )

    print("\nSUMMARY:", variable)

    if level_p < 0.05:
        print("Potentially I(0)")

    elif diff_p < 0.05:
        print("Potentially I(1)")

    elif second_p < 0.05:
        print("Potentially I(2) - requires caution")

    else:
        print("Integration order remains uncertain")

print("\nStationarity testing completed!")
