
import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

const API_URL = "http://127.0.0.1:5000";

function ModelComparison() {
  const [models, setModels] = useState([]);
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [metric, setMetric] = useState("rmse");

  useEffect(() => {
    async function fetchModels() {
      try {
        const response = await fetch(`${API_URL}/api/models`);

        if (!response.ok) {
          throw new Error("Unable to retrieve model results.");
        }

        const result = await response.json();

        setModels(result.data || []);
        setInfo(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchModels();
  }, []);

  const formatNumber = (value) =>
    Number(value).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });

  const bestModel = models.find((model) => model.rank === 1);

  const metricLabels = {
    mae: "Mean Absolute Error (MAE)",
    rmse: "Root Mean Squared Error (RMSE)",
    mape: "Mean Absolute Percentage Error (MAPE)",
  };

  const metricDescription = {
    mae: "Average absolute difference between actual and predicted remittances.",
    rmse: "Measures prediction error while giving more weight to larger errors.",
    mape: "Average prediction error expressed as a percentage.",
  };

  if (loading) {
    return <div className="loading">Loading model comparison...</div>;
  }

  if (error) {
    return <div className="error-box">Error: {error}</div>;
  }

  return (
    <>
      <header className="topbar">
        <div>
          <span className="breadcrumb">
            Dashboard / Model Comparison
          </span>

          <h1>Model Comparison</h1>

          <p>
            Evaluation and comparison of cash remittance
            forecasting models
          </p>
        </div>

        <div className="header-badge">
          12-Month Holdout Test
        </div>
      </header>

      <section className="section-heading">
        <h2>Forecasting Model Performance</h2>
        <p>
          Comparison using MAE, RMSE, and MAPE on the
          independent test period
        </p>
      </section>

      <section className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon blue">▦</div>
          <span className="kpi-label">Models Evaluated</span>
          <h2>{models.length}</h2>
          <p>Statistical and machine learning models</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon purple">★</div>
          <span className="kpi-label">Best Performing Model</span>
          <h2>{bestModel?.model || "N/A"}</h2>
          <p>Ranked by lowest test RMSE</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon green">◎</div>
          <span className="kpi-label">Best Test RMSE</span>
          <h2>
            {bestModel ? formatNumber(bestModel.rmse) : "N/A"}
          </h2>
          <p>Million USD</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon orange">%</div>
          <span className="kpi-label">Best Test MAPE</span>
          <h2>
            {bestModel ? `${formatNumber(bestModel.mape)}%` : "N/A"}
          </h2>
          <p>Average absolute percentage error</p>
        </div>
      </section>

      <section className="panel" style={{ marginTop: 28 }}>
        <div className="panel-header">
          <div>
            <h3>Model Performance Comparison</h3>
            <p>
              Select a metric to compare forecasting errors.
              Lower values indicate better performance.
            </p>
          </div>

          <select
            value={metric}
            onChange={(event) => setMetric(event.target.value)}
            style={{
              padding: "10px 14px",
              border: "1px solid #dbe3ef",
              borderRadius: 8,
              background: "white",
              color: "#102341",
              fontSize: 13,
            }}
          >
            <option value="rmse">RMSE</option>
            <option value="mae">MAE</option>
            <option value="mape">MAPE</option>
          </select>
        </div>

        <p style={{ color: "#64748b", fontSize: 13 }}>
          {metricDescription[metric]}
        </p>

        <div style={{ width: "100%", height: 350, marginTop: 20 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={models}
              layout="vertical"
              margin={{ top: 10, right: 45, left: 30, bottom: 10 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#e2e8f0"
              />

              <XAxis type="number" />

              <YAxis
                type="category"
                dataKey="model"
                width={110}
                tick={{ fontSize: 12 }}
              />

              <Tooltip
                formatter={(value) => [
                  `${formatNumber(value)}${metric === "mape" ? "%" : " million USD"}`,
                  metric.toUpperCase(),
                ]}
              />

              <Legend />

              <Bar
                dataKey={metric}
                name={metricLabels[metric]}
                fill="#2563eb"
                radius={[0, 6, 6, 0]}
                maxBarSize={35}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="panel" style={{ marginTop: 28 }}>
        <div className="panel-header">
          <div>
            <h3>Model Evaluation Results</h3>
            <p>
              Test period: {info?.evaluation_period || "July 2025 – June 2026"}
            </p>
          </div>

          <span>Lower error is better</span>
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
                {["Rank", "Model", "MAE", "RMSE", "MAPE", "Result"].map(
                  (heading) => (
                    <th
                      key={heading}
                      style={{
                        padding: 14,
                        color: "#334155",
                        borderBottom: "1px solid #e2e8f0",
                      }}
                    >
                      {heading}
                    </th>
                  )
                )}
              </tr>
            </thead>

            <tbody>
              {models.map((model) => (
                <tr key={model.model}>
                  <td style={cellStyle}>{model.rank}</td>

                  <td style={{ ...cellStyle, fontWeight: 600 }}>
                    {model.model}
                  </td>

                  <td style={cellStyle}>
                    {formatNumber(model.mae)}
                  </td>

                  <td style={cellStyle}>
                    {formatNumber(model.rmse)}
                  </td>

                  <td style={cellStyle}>
                    {formatNumber(model.mape)}%
                  </td>

                  <td style={cellStyle}>
                    {model.rank === 1 ? (
                      <span
                        style={{
                          color: "#15803d",
                          background: "#dcfce7",
                          padding: "6px 10px",
                          borderRadius: 6,
                          fontWeight: 600,
                        }}
                      >
                        Best Model
                      </span>
                    ) : (
                      <span style={{ color: "#64748b" }}>
                        Evaluated
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p style={{ marginTop: 16, color: "#64748b", fontSize: 12 }}>
          MAE and RMSE are measured in million USD. MAPE is
          expressed as a percentage.
        </p>
      </section>

      <section className="panel" style={{ marginTop: 28 }}>
        <div className="panel-header">
          <h3>Model Selection and Interpretation</h3>
        </div>

        <div style={{ marginTop: 18 }}>
          <h3 style={{ color: "#102341", marginBottom: 12 }}>
            Why was SARIMA selected?
          </h3>

          <p style={{ color: "#64748b", lineHeight: 1.8 }}>
            SARIMA achieved the lowest forecasting errors
            among the five evaluated models during the
            12-month holdout test. Its performance suggests
            that modeling seasonal patterns and historical
            remittance behavior is effective for this dataset.
          </p>

          <p
            style={{
              color: "#64748b",
              lineHeight: 1.8,
              marginTop: 12,
            }}
          >
            XGBoost A and XGBoost B also produced competitive
            results but had higher test errors than SARIMA.
            Seasonal Naive served as a benchmark, while ARIMA
            provided a non-seasonal statistical comparison.
          </p>

          <p
            style={{
              color: "#64748b",
              lineHeight: 1.8,
              marginTop: 12,
            }}
          >
            Based on the final evaluation, SARIMA was selected
            to generate the system's 12-month cash remittance
            forecasts for July 2026 through June 2027.
          </p>
        </div>
      </section>

      <p
        style={{
          textAlign: "center",
          color: "#94a3b8",
          fontSize: 12,
          padding: "28px 0",
        }}
      >
        RemitTrendPH · BSP & PSA Historical Data ·
        Forecasting results are statistical estimates.
      </p>
    </>
  );
}

const cellStyle = {
  padding: 14,
  borderBottom: "1px solid #e2e8f0",
  color: "#334155",
};

export default ModelComparison;
