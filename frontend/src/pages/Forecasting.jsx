
import { useEffect, useState } from "react";

import {
  ResponsiveContainer,
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

function Forecasting() {
  const [forecastData, setForecastData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [forecastInfo, setForecastInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadForecast() {
      try {
        const [forecastResponse, summaryResponse] =
          await Promise.all([
            fetch(`${API_URL}/api/forecast`),
            fetch(`${API_URL}/api/summary`),
          ]);

        if (!forecastResponse.ok || !summaryResponse.ok) {
          throw new Error("Failed to load forecasting data.");
        }

        const forecastResult = await forecastResponse.json();
        const summaryResult = await summaryResponse.json();

        const records = (forecastResult.data || []).map(
          (item) => ({
            month: item.month,
            forecast: Number(item.forecast),
            lower_95: Number(item.lower_95),
            upper_95: Number(item.upper_95),
            interval: [
              Number(item.lower_95),
              Number(item.upper_95),
            ],
          })
        );

        setForecastData(records);
        setForecastInfo(forecastResult);
        setSummary(summaryResult);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadForecast();
  }, []);

  const formatNumber = (value) =>
    Number(value).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });

  const formatMonth = (month) => {
    const [year, monthNumber] = month.split("-");
    const date = new Date(
      Number(year),
      Number(monthNumber) - 1,
      1
    );

    return date.toLocaleDateString("en-US", {
      month: "long",
      year: "numeric",
    });
  };

  if (loading) {
    return <p className="loading">Loading forecasts...</p>;
  }

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  return (
    <>
      {/* PAGE HEADER */}
      <header className="topbar">
        <div>
          <span className="breadcrumb">
            Dashboard / Forecasting
          </span>

          <h1>Remittance Forecasting</h1>

          <p>
            Twelve-month overseas Filipino cash remittance
            forecasts using the selected SARIMA model
          </p>
        </div>

        <div className="header-badge">
          July 2026 – June 2027
        </div>
      </header>

      {/* KPI SECTION */}
      <section className="section-heading">
        <h2>Forecast Summary</h2>
        <p>
          Projected monthly cash remittances for the next
          12 months
        </p>
      </section>

      <section className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon blue">▦</div>
          <span className="kpi-label">
            Forecast Horizon
          </span>
          <h2>{forecastData.length} Months</h2>
          <p>July 2026 – June 2027</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon green">↗</div>
          <span className="kpi-label">
            Total Forecasted Remittances
          </span>
          <h2>
            ${formatNumber(summary.forecast.total_forecast)}M
          </h2>
          <p>Combined forecast for 12 months</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon purple">★</div>
          <span className="kpi-label">
            Highest Forecast Month
          </span>
          <h2>
            {formatMonth(summary.forecast.highest_month)}
          </h2>
          <p>
            ${formatNumber(
              summary.forecast.highest_forecast
            )}M
          </p>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon orange">◎</div>
          <span className="kpi-label">
            Lowest Forecast Month
          </span>
          <h2>
            {formatMonth(summary.forecast.lowest_month)}
          </h2>
          <p>
            ${formatNumber(
              summary.forecast.lowest_forecast
            )}M
          </p>
        </div>
      </section>

      {/* FORECAST CHART */}
      <section className="panel" style={{ marginTop: 28 }}>
        <div className="panel-header">
          <div>
            <h3>12-Month SARIMA Forecast</h3>
            <p>
              Predicted monthly remittances with 95%
              prediction intervals
            </p>
          </div>
          <span>SARIMA</span>
        </div>

        <div style={{ width: "100%", height: 390, marginTop: 24 }}>
          <ResponsiveContainer width="100%" height="100%">
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
                  const [year, month] = value.split("-");
                  return `${month}/${year.slice(2)}`;
                }}
                tick={{ fontSize: 12 }}
              />

              <YAxis
                width={65}
                domain={["auto", "auto"]}
                tick={{ fontSize: 12 }}
              />

              <Tooltip
                labelFormatter={(value) =>
                  formatMonth(value)
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

              <Area
                type="linear"
                dataKey="interval"
                name="95% Prediction Interval"
                stroke="none"
                fill="#93c5fd"
                fillOpacity={0.35}
                isAnimationActive={false}
              />

              <Line
                type="linear"
                dataKey="forecast"
                name="SARIMA Forecast"
                stroke="#2563eb"
                strokeWidth={3}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <p className="forecast-note">
          Forecasts are statistical estimates. The shaded
          region represents model-based uncertainty using
          95% prediction intervals.
        </p>
      </section>

      {/* MONTHLY FORECAST TABLE */}
      <section className="panel" style={{ marginTop: 28 }}>
        <div className="panel-header">
          <div>
            <h3>Monthly Forecast Results</h3>
            <p>
              Detailed predictions and prediction intervals
              in million USD
            </p>
          </div>
        </div>

        <div style={{ overflowX: "auto", marginTop: 20 }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              textAlign: "left",
              fontSize: 14,
            }}
          >
            <thead>
              <tr style={{ background: "#f1f5f9" }}>
                {[
                  "Month",
                  "Forecast (Million USD)",
                  "Lower 95%",
                  "Upper 95%",
                ].map((heading) => (
                  <th
                    key={heading}
                    style={{
                      padding: 14,
                      borderBottom: "1px solid #e2e8f0",
                    }}
                  >
                    {heading}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {forecastData.map((item) => (
                <tr key={item.month}>
                  <td style={cellStyle}>
                    {formatMonth(item.month)}
                  </td>

                  <td style={cellStyle}>
                    ${formatNumber(item.forecast)}
                  </td>

                  <td style={cellStyle}>
                    ${formatNumber(item.lower_95)}
                  </td>

                  <td style={cellStyle}>
                    ${formatNumber(item.upper_95)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* FORECAST INTERPRETATION */}
      <section className="panel" style={{ marginTop: 28 }}>
        <div className="panel-header">
          <h3>Forecast Interpretation</h3>
        </div>

        <div style={{ marginTop: 16, lineHeight: 1.8 }}>
          <p>
            The RemitTrendPH system uses SARIMA to forecast
            monthly overseas Filipino cash remittances.
            SARIMA was selected because it achieved the
            lowest forecasting error during the independent
            12-month holdout test.
          </p>

          <p style={{ marginTop: 12 }}>
            The forecast covers July 2026 through June 2027.
            December 2026 is projected to have the highest
            monthly remittances, while May 2027 is projected
            to have the lowest.
          </p>

          <p style={{ marginTop: 12 }}>
            These predictions are intended to support trend
            analysis and planning. Actual remittance values
            may differ from the forecasts.
          </p>
        </div>
      </section>

      <footer className="footer">
        RemitTrendPH · BSP & PSA Historical Data ·
        Forecasts are estimates, not guaranteed outcomes.
      </footer>
    </>
  );
}

const cellStyle = {
  padding: 14,
  borderBottom: "1px solid #e2e8f0",
  color: "#334155",
};

export default Forecasting;
