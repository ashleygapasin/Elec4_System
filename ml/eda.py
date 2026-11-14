
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Locate the project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Load the cleaned dataset
file_path = BASE_DIR / "data" / "processed" / "final_dataset.csv"

df = pd.read_csv(file_path)

# Convert month to datetime
df["month"] = pd.to_datetime(df["month"])

# Sort by month
df = df.sort_values("month")

# Display basic information
print("DATASET INFORMATION:")
print(df.info())

print("\nSUMMARY STATISTICS:")
print(df[["cash", "php_per_usd", "cpi", "inflation_yoy"]].describe())

# Plot historical cash remittances
plt.figure(figsize=(12, 5))

plt.plot(
    df["month"],
    df["cash"],
    marker="o",
    markersize=3
)

plt.title("Monthly Overseas Filipino Cash Remittances (2019–2026)")
plt.xlabel("Year")
plt.ylabel("Cash Remittances (Million USD)")
plt.grid(True)

plt.tight_layout()
plt.show()


# STEP 2: MONTHLY SEASONALITY ANALYSIS

# Extract month name
df["month_name"] = df["month"].dt.month_name()

# Calculate average remittances for each month
monthly_average = df.groupby(
    df["month"].dt.month
)["cash"].mean()

# Month labels
month_labels = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

# Display monthly averages
print("\nAVERAGE CASH REMITTANCES BY MONTH:")
print(monthly_average)

# Create bar chart
plt.figure(figsize=(12, 5))

plt.bar(
    month_labels,
    monthly_average.values
)

plt.title("Average Monthly Cash Remittances (2019–2026)")
plt.xlabel("Month")
plt.ylabel("Average Cash Remittances (Million USD)")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.show()


# STEP 3: SEASONAL DECOMPOSITION

from statsmodels.tsa.seasonal import seasonal_decompose

# Set the month as the index
time_series = df.set_index("month")["cash"]

# Decompose into trend, seasonality, and residual
decomposition = seasonal_decompose(
    time_series,
    model="additive",
    period=12
)

# Display decomposition graphs
fig = decomposition.plot()

fig.set_size_inches(12, 9)
fig.suptitle(
    "Seasonal Decomposition of OFW Cash Remittances",
    fontsize=14
)

plt.tight_layout()
plt.show()


# STEP 4: 12-MONTH MOVING AVERAGE

# Calculate the average of the previous 12 months
# including the current month
df["moving_average_12"] = df["cash"].rolling(
    window=12
).mean()

# Plot actual remittances and moving average
plt.figure(figsize=(12, 5))

plt.plot(
    df["month"],
    df["cash"],
    label="Actual Cash Remittances",
    alpha=0.5
)

plt.plot(
    df["month"],
    df["moving_average_12"],
    label="12-Month Moving Average",
    linewidth=2
)

plt.title("Cash Remittances with 12-Month Moving Average")
plt.xlabel("Year")
plt.ylabel("Cash Remittances (Million USD)")
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
