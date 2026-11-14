
import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";



const API_URL = "http://127.0.0.1:5000";

function Overview() {
  const [summary, setSummary] = useState(null);
  const [historical, setHistorical] = useState([]);
  const [forecastData, setForecastData] = useState([]);

  const [error, setError] = useState("");
  const [historicalError, setHistoricalError] = useState("");
  const [forecastError, setForecastError] = useState("");

  // Load dashboard summary
  useEffect(() => {
    fetch(`${API_URL}/api/summary`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load dashboard summary");
        }
        return response.json();
      })
      .then((data) => setSummary(data))
      .catch((err) => setError(err.message));
  }, []);

  // Load historical remittance records
  useEffect(() => {
    fetch(`${API_URL}/api/remittances`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load historical data");
        }
        return response.json();
      })
      .then((result) => {
        const records = result.data.map((item) => ({
          month: item.month,
          cash: Number(item.cash),
        }));

        setHistorical(records);
      })
      .catch((err) => setHistoricalError(err.message));
  }, []);

  // Load 12-month SARIMA forecasts
  useEffect(() => {
    fetch(`${API_URL}/api/forecast`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load forecast data");
        }
        return response.json();
      })
      .then((result) => {
        const records = result.data.map((item) => ({
          month: item.month,
          forecast: Number(item.forecast),
          lower_95: Number(item.lower_95),
          upper_95: Number(item.upper_95),
          interval: [
            Number(item.lower_95),
            Number(item.upper_95),
          ],
        }));

        setForecastData(records);
      })
      .catch((err) => setForecastError(err.message));
  }, []);

  // Format numerical values
  const formatNumber = (value) =>
    Number(value).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });

  return (
  <>
    <header className="topbar">
          <div>
            <span className="breadcrumb">
              Dashboard / Overview
            </span>

            <h1>Dashboard Overview</h1>

            <p>
              Overseas Filipino Cash Remittance Forecasting
              and Trend Analytics
            </p>
          </div>

          <div className="header-badge">
            Historical Data: 2019–2026
          </div>
        </header>

        {error && (
          <div className="error-box">{error}</div>
        )}

        {!summary && !error && (
          <p className="loading">Loading dashboard...</p>
        )}

        {summary && (
          <>
            {/* KPI SECTION */}
            <section className="section-heading">
              <h2>Key Performance Indicators</h2>

              <p>
                Overview of remittance data and forecasting
                performance
              </p>
            </section>

            <section className="kpi-grid">
              <div className="kpi-card">
                <div className="kpi-icon blue">▦</div>

                <span className="kpi-label">
                  Historical Observations
                </span>

                <h2>
                  {summary.historical.total_months}
                </h2>

                <p>
                  Monthly records ·{" "}
                  {summary.historical.start_month} to{" "}
                  {summary.historical.end_month}
                </p>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon green">₱</div>

                <span className="kpi-label">
                  Latest Cash Remittances
                </span>

                <h2>
                  $
                  {formatNumber(
                    summary.historical.latest_cash
                  )}
                  M
                </h2>

                <p>
                  As of {summary.historical.end_month}
                  {summary.historical.latest_data_preliminary
                    ? " · Preliminary"
                    : ""}
                </p>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon purple">★</div>

                <span className="kpi-label">
                  Best Forecasting Model
                </span>

                <h2>
                  {summary.best_model.name}
                </h2>

                <p>
                  Test RMSE: {summary.best_model.rmse}{" "}
                  million USD
                </p>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon orange">◎</div>

                <span className="kpi-label">
                  Forecast Accuracy (Test MAPE)
                </span>

                <h2>
                  {summary.best_model.mape}%
                </h2>

                <p>
                  Lower MAPE indicates better performance
                </p>
              </div>
            </section>

            {/* HISTORICAL CHART AND FORECAST SUMMARY */}
            <section className="dashboard-grid">
              <div className="panel">
                <div className="panel-header">
                  <h3>Historical Remittance Trends</h3>
                  <span>2019 – 2026</span>
                </div>

                <div className="chart-container">
                  {historicalError ? (
                    <p className="chart-message">
                      {historicalError}
                    </p>
                  ) : historical.length === 0 ? (
                    <p className="chart-message">
                      Loading historical chart...
                    </p>
                  ) : (
                    <ResponsiveContainer
                      width="100%"
                      height="100%"
                    >
                      <LineChart
                        data={historical}
                        margin={{
                          top: 10,
                          right: 20,
                          left: 5,
                          bottom: 10,
                        }}
                      >
                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="#e2e8f0"
                        />

                        <XAxis
                          dataKey="month"
                          tickFormatter={(value) =>
                            value.slice(0, 4)
                          }
                          minTickGap={35}
                          tick={{ fontSize: 11 }}
                        />

                        <YAxis
                          tick={{ fontSize: 11 }}
                          width={55}
                          domain={["auto", "auto"]}
                        />

                        <Tooltip
                          labelFormatter={(value) =>
                            `Month: ${value}`
                          }
                          formatter={(value) => [
                            `$${formatNumber(value)} million`,
                            "Cash Remittances",
                          ]}
                        />

                        <Line
                          type="monotone"
                          dataKey="cash"
                          stroke="#2563eb"
                          strokeWidth={2.5}
                          dot={false}
                          activeDot={{ r: 5 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </div>

              {/* FORECAST SUMMARY */}
              <div className="panel">
                <div className="panel-header">
                  <h3>12-Month Forecast Summary</h3>
                  <span>SARIMA</span>
                </div>

                <div className="forecast-stat">
                  <span>
                    Total Predicted Remittances
                  </span>

                  <h2>
                    $
                    {formatNumber(
                      summary.forecast.total_forecast
                    )}
                    M
                  </h2>
                </div>

                <div className="forecast-details">
                  <div>
                    <span>Forecast Period</span>
                    <strong>
                      {summary.forecast.start_month} to{" "}
                      {summary.forecast.end_month}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Highest Forecast Month
                    </span>
                    <strong>
                      {summary.forecast.highest_month}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Lowest Forecast Month
                    </span>
                    <strong>
                      {summary.forecast.lowest_month}
                    </strong>
                  </div>

                  <div>
                    <span>Forecast Horizon</span>
                    <strong>
                      {summary.forecast.total_months}{" "}
                      months
                    </strong>
                  </div>
                </div>
              </div>
            </section>

            {/* SARIMA FORECAST CHART */}
            <section className="forecast-chart-section">
              <div className="panel">
                <div className="panel-header">
                  <h3>
                    12-Month Cash Remittance Forecast
                  </h3>

                  <span>
                    SARIMA · July 2026 – June 2027
                  </span>
                </div>

                <p className="chart-description">
                  Monthly cash remittance predictions with
                  95% prediction intervals. Values are
                  expressed in million USD.
                </p>

                <div className="forecast-chart-container">
                  {forecastError ? (
                    <p className="chart-message">
                      {forecastError}
                    </p>
                  ) : forecastData.length === 0 ? (
                    <p className="chart-message">
                      Loading forecast chart...
                    </p>
                  ) : (
                    <ResponsiveContainer
                      width="100%"
                      height="100%"
                    >
                      <ComposedChart
                        data={forecastData}
                        margin={{
                          top: 15,
                          right: 25,
                          left: 10,
                          bottom: 10,
                        }}
                      >
                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="#e2e8f0"
                        />

                        <XAxis
                          dataKey="month"
                          tickFormatter={(value) => {
                            const [year, month] =
                              value.split("-");

                            return `${month}/${year.slice(2)}`;
                          }}
                          tick={{ fontSize: 11 }}
                          minTickGap={20}
                        />

                        <YAxis
                          tick={{ fontSize: 11 }}
                          width={60}
                          domain={["auto", "auto"]}
                        />

                        <Tooltip
                          labelFormatter={(value) =>
                            `Month: ${value}`
                          }
                          formatter={(value, name) => {
                            if (Array.isArray(value)) {
                              return [
                                `$${formatNumber(value[0])}M – $${formatNumber(value[1])}M`,
                                "95% Prediction Interval",
                              ];
                            }

                            return [
                              `$${formatNumber(value)}M`,
                              name,
                            ];
                          }}
                        />

                        <Legend />

                        {/* SHADED 95% PREDICTION INTERVAL */}
                        <Area
                          type="linear"
                          dataKey="interval"
                          name="95% Prediction Interval"
                          stroke="none"
                          fill="#93c5fd"
                          fillOpacity={0.35}
                          isAnimationActive={false}
                        />

                        {/* SARIMA FORECAST LINE */}
                        <Line
                          type="linear"
                          dataKey="forecast"
                          name="SARIMA Forecast"
                          stroke="#2563eb"
                          strokeWidth={3}
                          dot={{ r: 3 }}
                          activeDot={{ r: 6 }}
                        />
                      </ComposedChart>
                    </ResponsiveContainer>
                  )}
                </div>

                <p className="forecast-note">
                  Forecasts are statistical estimates.
                  Prediction intervals represent model-based
                  uncertainty and do not guarantee actual
                  remittance values.
                </p>
              </div>
            </section>

            <footer className="footer">
              RemitTrendPH · BSP & PSA Historical Data ·
              Forecasts are estimates, not guaranteed
              outcomes.
            </footer>
          </>
        )}
  </>
  );
}

export default Overview;
