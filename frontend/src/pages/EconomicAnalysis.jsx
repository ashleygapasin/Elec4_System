
import { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceLine,
} from "recharts";

const API_URL = "http://127.0.0.1:5000/api/remittances";

const cardStyle = {
  background: "#ffffff",
  border: "1px solid #e2e8f0",
  borderRadius: "12px",
  padding: "20px",
};

const sectionStyle = {
  ...cardStyle,
  marginTop: "24px",
};

const formatNumber = (value, digits = 2) => {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) {
    return "N/A";
  }

  return Number(value).toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
};

const toNumber = (value) => {
  if (value === null || value === undefined || value === "") {
    return null;
  }

  const number = Number(value);
  return Number.isFinite(number) ? number : null;
};

// Pearson correlation coefficient
function calculateCorrelation(data, xKey, yKey) {
  const pairs = data
    .filter(
      (item) =>
        Number.isFinite(item[xKey]) &&
        Number.isFinite(item[yKey])
    )
    .map((item) => [item[xKey], item[yKey]]);

  const n = pairs.length;

  if (n < 3) return null;

  const meanX = pairs.reduce((sum, pair) => sum + pair[0], 0) / n;
  const meanY = pairs.reduce((sum, pair) => sum + pair[1], 0) / n;

  let numerator = 0;
  let sumX = 0;
  let sumY = 0;

  pairs.forEach(([x, y]) => {
    const dx = x - meanX;
    const dy = y - meanY;

    numerator += dx * dy;
    sumX += dx * dx;
    sumY += dy * dy;
  });

  const denominator = Math.sqrt(sumX * sumY);

  if (denominator === 0) return null;

  return {
    value: numerator / denominator,
    observations: n,
  };
}

function interpretCorrelation(value) {
  if (value === null) return "Insufficient data";

  const strength = Math.abs(value);

  let description;

  if (strength < 0.2) {
    description = "Very weak";
  } else if (strength < 0.4) {
    description = "Weak";
  } else if (strength < 0.6) {
    description = "Moderate";
  } else if (strength < 0.8) {
    description = "Strong";
  } else {
    description = "Very strong";
  }

  if (value === 0) return "No linear correlation";

  return `${description} ${value > 0 ? "positive" : "negative"} correlation`;
}

function EconomicAnalysis() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const response = await fetch(API_URL);

        if (!response.ok) {
          throw new Error("Failed to load economic data from the backend.");
        }

        const result = await response.json();

        if (!Array.isArray(result.data)) {
          throw new Error("Invalid API response format.");
        }

        setRecords(result.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const data = useMemo(() => {
    return records
      .filter(
        (item) =>
          item.month &&
          toNumber(item.cash) !== null
      )
      .map((item) => ({
        month: String(item.month).slice(0, 7),
        cash: toNumber(item.cash),
        exchangeRate: toNumber(item.php_per_usd),
        inflation: toNumber(item.inflation_yoy),
        cpi: toNumber(item.cpi),
        preliminary: item.preliminary,
      }))
      .sort((a, b) => a.month.localeCompare(b.month));
  }, [records]);

  const latest = data.length ? data[data.length - 1] : null;

  const exchangeCorrelation = useMemo(
    () => calculateCorrelation(data, "exchangeRate", "cash"),
    [data]
  );

  const inflationCorrelation = useMemo(
    () => calculateCorrelation(data, "inflation", "cash"),
    [data]
  );

  const exchangeScatter = useMemo(
    () =>
      data
        .filter(
          (item) =>
            item.exchangeRate !== null &&
            item.cash !== null
        )
        .map((item) => ({
          month: item.month,
          x: item.exchangeRate,
          y: item.cash,
        })),
    [data]
  );

  const inflationScatter = useMemo(
    () =>
      data
        .filter(
          (item) =>
            item.inflation !== null &&
            item.cash !== null
        )
        .map((item) => ({
          month: item.month,
          x: item.inflation,
          y: item.cash,
        })),
    [data]
  );

  if (loading) {
    return <p>Loading Economic Analysis...</p>;
  }

  if (error) {
    return <p style={{ color: "#dc2626" }}>Error: {error}</p>;
  }

  if (!latest) {
    return <p>No economic data available.</p>;
  }

  return (
    <div style={{ padding: "8px 0 32px" }}>
      <h1 style={{ color: "#0f172a", marginBottom: "8px" }}>
        Economic Analysis
      </h1>

      <p style={{ color: "#64748b", marginBottom: "24px" }}>
        Explore historical relationships between Philippine cash
        remittances, exchange rates, and inflation.
      </p>

      {/* SUMMARY CARDS */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(210px, 1fr))",
          gap: "16px",
        }}
      >
        <div style={cardStyle}>
          <p style={{ color: "#64748b" }}>Latest Exchange Rate</p>
          <h2>₱{formatNumber(latest.exchangeRate)}</h2>
          <small>PHP per USD · {latest.month}</small>
        </div>

        <div style={cardStyle}>
          <p style={{ color: "#64748b" }}>Latest Inflation Rate</p>
          <h2>{formatNumber(latest.inflation)}%</h2>
          <small>Year-over-year · {latest.month}</small>
        </div>

        <div style={cardStyle}>
          <p style={{ color: "#64748b" }}>Exchange Rate Correlation</p>
          <h2>
            {exchangeCorrelation
              ? formatNumber(exchangeCorrelation.value, 3)
              : "N/A"}
          </h2>
          <small>
            {interpretCorrelation(exchangeCorrelation?.value ?? null)}
          </small>
        </div>

        <div style={cardStyle}>
          <p style={{ color: "#64748b" }}>Inflation Correlation</p>
          <h2>
            {inflationCorrelation
              ? formatNumber(inflationCorrelation.value, 3)
              : "N/A"}
          </h2>
          <small>
            {interpretCorrelation(inflationCorrelation?.value ?? null)}
          </small>
        </div>
      </div>

      {/* EXCHANGE RATE TREND */}
      <section style={sectionStyle}>
        <h2>Historical Exchange Rate Trend</h2>
        <p style={{ color: "#64748b" }}>
          Monthly average Philippine peso per US dollar.
        </p>

        <div style={{ width: "100%", height: 340 }}>
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                minTickGap={35}
                tick={{ fontSize: 11 }}
              />
              <YAxis
                domain={["auto", "auto"]}
                tick={{ fontSize: 11 }}
              />
              <Tooltip
                formatter={(value) => [
                  `₱${formatNumber(value)}`,
                  "PHP/USD",
                ]}
              />
              <Line
                type="monotone"
                dataKey="exchangeRate"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
                connectNulls={false}
                name="PHP/USD Exchange Rate"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* INFLATION TREND */}
      <section style={sectionStyle}>
        <h2>Historical Inflation Trend</h2>
        <p style={{ color: "#64748b" }}>
          Philippine year-over-year inflation rate.
        </p>

        <div style={{ width: "100%", height: 340 }}>
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                minTickGap={35}
                tick={{ fontSize: 11 }}
              />
              <YAxis
                tickFormatter={(value) => `${value}%`}
                tick={{ fontSize: 11 }}
              />
              <Tooltip
                formatter={(value) => [
                  `${formatNumber(value)}%`,
                  "Inflation",
                ]}
              />
              <ReferenceLine y={0} stroke="#94a3b8" />
              <Line
                type="monotone"
                dataKey="inflation"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
                connectNulls={false}
                name="Inflation Rate"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* REMITTANCES VS EXCHANGE RATE */}
      <section style={sectionStyle}>
        <h2>Remittances vs. Exchange Rate</h2>
        <p style={{ color: "#64748b" }}>
          Compare historical cash remittances and PHP/USD
          exchange-rate movements.
        </p>

        <div style={{ width: "100%", height: 350 }}>
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                minTickGap={35}
                tick={{ fontSize: 11 }}
              />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 11 }}
                label={{
                  value: "Million USD",
                  angle: -90,
                  position: "insideLeft",
                }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                domain={["auto", "auto"]}
                tick={{ fontSize: 11 }}
                label={{
                  value: "PHP/USD",
                  angle: 90,
                  position: "insideRight",
                }}
              />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="cash"
                name="Cash Remittances (M USD)"
                stroke="#2563eb"
                dot={false}
                strokeWidth={2}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="exchangeRate"
                name="Exchange Rate (PHP/USD)"
                stroke="#16a34a"
                dot={false}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* REMITTANCES VS INFLATION */}
      <section style={sectionStyle}>
        <h2>Remittances vs. Inflation</h2>
        <p style={{ color: "#64748b" }}>
          Compare remittance movements and year-over-year inflation.
        </p>

        <div style={{ width: "100%", height: 350 }}>
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                minTickGap={35}
                tick={{ fontSize: 11 }}
              />
              <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
              <YAxis
                yAxisId="right"
                orientation="right"
                tickFormatter={(value) => `${value}%`}
                tick={{ fontSize: 11 }}
              />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="cash"
                name="Cash Remittances (M USD)"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="inflation"
                name="Inflation Rate (%)"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
                connectNulls={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* CORRELATION SCATTER PLOTS */}
      <section style={sectionStyle}>
        <h2>Correlation Analysis</h2>
        <p style={{ color: "#64748b" }}>
          Pearson correlation measures the strength and
          direction of a linear relationship.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "20px",
          }}
        >
          <div>
            <h3>Exchange Rate and Remittances</h3>
            <div style={{ height: 320, width: "100%" }}>
              <ResponsiveContainer>
                <ScatterChart margin={{ bottom: 10, right: 15 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="PHP/USD"
                    domain={["auto", "auto"]}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name="Remittances"
                    domain={["auto", "auto"]}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3" }}
                    formatter={(value) => formatNumber(value)}
                  />
                  <Scatter
                    data={exchangeScatter}
                    fill="#2563eb"
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <p>
              Correlation:{" "}
              <strong>
                {exchangeCorrelation
                  ? formatNumber(exchangeCorrelation.value, 3)
                  : "N/A"}
              </strong>
            </p>
          </div>

          <div>
            <h3>Inflation and Remittances</h3>
            <div style={{ height: 320, width: "100%" }}>
              <ResponsiveContainer>
                <ScatterChart margin={{ bottom: 10, right: 15 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="Inflation (%)"
                    domain={["auto", "auto"]}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name="Remittances"
                    domain={["auto", "auto"]}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3" }}
                    formatter={(value) => formatNumber(value)}
                  />
                  <Scatter
                    data={inflationScatter}
                    fill="#f59e0b"
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <p>
              Correlation:{" "}
              <strong>
                {inflationCorrelation
                  ? formatNumber(inflationCorrelation.value, 3)
                  : "N/A"}
              </strong>
            </p>
          </div>
        </div>
      </section>

      {/* INTERPRETATION */}
      <section style={sectionStyle}>
        <h2>Economic Analysis Insights</h2>

        <p>
          <strong>Exchange rate relationship:</strong>{" "}
          {interpretCorrelation(exchangeCorrelation?.value ?? null)}.
          {" "}This calculation uses{" "}
          {exchangeCorrelation?.observations ?? 0} paired observations.
        </p>

        <p>
          <strong>Inflation relationship:</strong>{" "}
          {interpretCorrelation(inflationCorrelation?.value ?? null)}.
          {" "}This calculation uses{" "}
          {inflationCorrelation?.observations ?? 0} paired observations.
        </p>

        <p>
          <strong>Latest available data:</strong>{" "}
          {latest.month}, with an exchange rate of ₱
          {formatNumber(latest.exchangeRate)} per USD and
          an inflation rate of {formatNumber(latest.inflation)}%.
        </p>

        <p style={{ color: "#64748b" }}>
          Note: Correlations are descriptive and do not prove
          causation. Common time trends, seasonality, and
          autocorrelation may influence the results. These
          calculations are not used to train or select the
          forecasting models. Recent data may be preliminary.
        </p>
      </section>
    </div>
  );
}

export default EconomicAnalysis;
