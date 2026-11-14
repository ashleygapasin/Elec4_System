
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from pathlib import Path

# STEP 1: CREATE FLASK APPLICATION
app = Flask(__name__)

# Allow React frontend to communicate with Flask
CORS(app)

# STEP 2: DEFINE PROJECT PATHS
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR / "data" / "processed" / "final_dataset.csv"
)

# STEP 3: HOME ROUTE
@app.route("/")
def home():
    return jsonify({
        "system": "RemitTrendPH",
        "message": "Backend API is running successfully!"
    })


# STEP 4: HISTORICAL REMITTANCE ROUTE
@app.route("/api/remittances")
def get_remittances():

    df = pd.read_csv(DATA_FILE)

    # Convert missing values into JSON-compatible nulls
    df = df.astype(object).where(pd.notna(df), None)

    records = df.to_dict(orient="records")

    return jsonify({
        "total_records": len(records),
        "data": records
    })


# STEP 6: SARIMA FORECAST ROUTE
@app.route("/api/forecast")
def get_forecast():

    forecast_file = (
        BASE_DIR
        / "artifacts"
        / "forecasts"
        / "sarima_future_12_months.csv"
    )

    df = pd.read_csv(forecast_file)

    records = df.to_dict(orient="records")

    return jsonify({
        "model": "SARIMA",
        "order": [1, 1, 1],
        "seasonal_order": [1, 1, 0, 12],
        "forecast_origin": "2026-06-01",
        "forecast_period": "July 2026 - June 2027",
        "unit": "Million USD",
        "total_months": len(records),
        "data": records
    })


# STEP 7: MODEL COMPARISON ROUTE
@app.route("/api/models")
def get_models():

    metrics_file = (
        BASE_DIR
        / "artifacts"
        / "model_comparison"
        / "final_test_metrics.csv"
    )

    df = pd.read_csv(metrics_file)

    # Sort models by RMSE (lowest is best)
    df = df.sort_values(
        "rmse"
    ).reset_index(drop=True)

    # Add ranking
    df["rank"] = df.index + 1

    records = df.to_dict(orient="records")

    return jsonify({
        "evaluation_period": "July 2025 - June 2026",
        "evaluation_type": "12-month holdout test",
        "metrics": ["MAE", "RMSE", "MAPE"],
        "error_unit": "Million USD",
        "total_models": len(records),
        "best_model": records[0]["model"],
        "data": records
    })


# STEP 8: ARDL ECONOMIC ANALYSIS ROUTE
@app.route("/api/ardl")
def get_ardl():

    ardl_dir = BASE_DIR / "artifacts" / "ardl"

    coefficients_file = (
        ardl_dir / "ardl_coefficients.csv"
    )

    diagnostics_file = (
        ardl_dir / "ardl_diagnostics.csv"
    )

    # Load saved ARDL results
    coefficients_df = pd.read_csv(coefficients_file)
    diagnostics_df = pd.read_csv(diagnostics_file)

    # Convert missing values to JSON null
    coefficients_df = coefficients_df.astype(object).where(
        pd.notna(coefficients_df), None
    )

    diagnostics_df = diagnostics_df.astype(object).where(
        pd.notna(diagnostics_df), None
    )

    return jsonify({
        "model": "Seasonal ARDL(3,0)",
        "analysis_type": "Exploratory economic relationship analysis",
        "dependent_variable": "Cash Remittances",
        "selected_explanatory_variables": [
            "PHP/USD Exchange Rate"
        ],
        "excluded_by_aic": [
            "Inflation YoY"
        ],
        "significance_level": 0.05,
        "long_run_relationship_established": False,
        "limitations": [
            "Inflation integration order remains uncertain.",
            "ARDL bounds testing has not been completed.",
            "Residual normality was rejected.",
            "Coefficients do not establish causation."
        ],
        "coefficients": coefficients_df.to_dict(
            orient="records"
        ),
        "diagnostics": diagnostics_df.to_dict(
            orient="records"
        )
    })


# STEP 9: DASHBOARD SUMMARY ROUTE
@app.route("/api/summary")
def get_summary():

    # Load historical data
    historical_file = (
        BASE_DIR / "data" / "processed" / "final_dataset.csv"
    )

    # Load future forecasts
    forecast_file = (
        BASE_DIR / "artifacts" / "forecasts"
        / "sarima_future_12_months.csv"
    )

    # Load final model evaluation
    metrics_file = (
        BASE_DIR / "artifacts" / "model_comparison"
        / "final_test_metrics.csv"
    )

    historical = pd.read_csv(historical_file)
    forecast = pd.read_csv(forecast_file)
    metrics = pd.read_csv(metrics_file)

    # Convert dates
    historical["month"] = pd.to_datetime(
        historical["month"]
    )

    forecast["month"] = pd.to_datetime(
        forecast["month"]
    )

    # Sort records chronologically
    historical = historical.sort_values("month")
    forecast = forecast.sort_values("month")

    # Select the model with lowest test RMSE
    best = metrics.sort_values("rmse").iloc[0]

    # Latest historical record
    latest = historical.iloc[-1]

    # Highest and lowest forecast
    highest = forecast.loc[
        forecast["forecast"].idxmax()
    ]

    lowest = forecast.loc[
        forecast["forecast"].idxmin()
    ]

    return jsonify({
        "historical": {
            "total_months": len(historical),
            "start_month": historical["month"].min().strftime("%Y-%m"),
            "end_month": historical["month"].max().strftime("%Y-%m"),
            "latest_cash": round(float(latest["cash"]), 2),
            "latest_exchange_rate": round(
                float(latest["php_per_usd"]), 2
            ),
            "latest_inflation": round(
                float(latest["inflation_yoy"]), 2
            ),
            "latest_data_preliminary": bool(
                latest["preliminary"]
            ) if isinstance(
                latest["preliminary"], bool
            ) else str(latest["preliminary"]).lower() == "true"
        },

        "forecast": {
            "total_months": len(forecast),
            "start_month": forecast["month"].min().strftime("%Y-%m"),
            "end_month": forecast["month"].max().strftime("%Y-%m"),
            "total_forecast": round(
                float(forecast["forecast"].sum()), 2
            ),
            "average_monthly_forecast": round(
                float(forecast["forecast"].mean()), 2
            ),
            "highest_month": highest["month"].strftime("%Y-%m"),
            "highest_forecast": round(
                float(highest["forecast"]), 2
            ),
            "lowest_month": lowest["month"].strftime("%Y-%m"),
            "lowest_forecast": round(
                float(lowest["forecast"]), 2
            ),
            "unit": "Million USD"
        },

        "best_model": {
            "name": best["model"],
            "mae": round(float(best["mae"]), 2),
            "rmse": round(float(best["rmse"]), 2),
            "mape": round(float(best["mape"]), 2),
            "evaluation_period": "July 2025 - June 2026"
        }
    })


# STEP 5: RUN FLASK SERVER
if __name__ == "__main__":
    app.run(debug=True, port=5000)

