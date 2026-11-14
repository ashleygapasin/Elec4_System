
import { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";

const API_URL = "http://127.0.0.1:5000/api/remittances";

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

const formatMoney = (value) =>
  Number(value).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

const formatPercent = (value) =>
  value === null || !Number.isFinite(value)
    ? "N/A"
    : `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;

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

function SeasonalAnalysis() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const response = await fetch(API_URL);

        if (!response.ok) {
          throw new Error("Unable to load remittance data.");
        }

        const result = await response.json();

        if (!Array.isArray(result.data)) {
          throw new Error("Unexpected API response format.");
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
          item.cash !== null &&
          item.cash !== "" &&
          Number.isFinite(Number(item.cash))
      )
      .map((item) => ({
        ...item,
        cash: Number(item.cash),
        month: String(item.month).slice(0, 7),
      }))
      .sort((a, b) => a.month.localeCompare(b.month));
  }, [records]);

  const seasonalData = useMemo(() => {
    return MONTHS.map((name, index) => {
      const values = data
        .filter(
          (item) => Number(item.month.slice(5, 7)) === index + 1
        )
        .map((item) => item.cash);

      const average = values.length
        ? values.reduce((sum, value) => sum + value, 0) /
          values.length
        : null;

      return {
        month: name,
        average: average === null ? null : Number(average.toFixed(2)),
        observations: values.length,
      };
    });
  }, [data]);

  const yearlyComparison = useMemo(() => {
    const byMonth = {};

    data.forEach((item) => {
      const year = item.month.slice(0, 4);
      const monthNumber = Number(item.month.slice(5, 7));
      const monthName = MONTHS[monthNumber - 1];

      if (!byMonth[monthName]) {
        byMonth[monthName] = { month: monthName };
      }

      byMonth[monthName][year] = item.cash;
    });

    return MONTHS.map(
      (month) => byMonth[month] || { month }
    );
  }, [data]);

  const years = useMemo(
    () => [...new Set(data.map((item) => item.month.slice(0, 4)))],
    [data]
  );

  const yoyData = useMemo(() => {
    const lookup = new Map(
      data.map((item) => [item.month, item.cash])
    );

    return data.map((item) => {
      const year = Number(item.month.slice(0, 4));
      const month = item.month.slice(5, 7);
      const previous = lookup.get(`${year - 1}-${month}`);

      const yoy =
        previous !== undefined && previous !== 0
          ? ((item.cash - previous) / previous) * 100
          : null;

      return {
        month: item.month,
        yoy: yoy === null ? null : Number(yoy.toFixed(2)),
      };
    });
  }, [data]);

  const summary = useMemo(() => {
    if (!data.length) return null;

    const latest = data[data.length - 1];
    const latestYoY = yoyData[yoyData.length - 1]?.yoy ?? null;

    const availableMonths = seasonalData.filter(
      (item) => item.average !== null
    );

    const highest = availableMonths.reduce(
      (best, item) =>
        !best || item.average > best.average ? item : best,
      null
    );

    const lowest = availableMonths.reduce(
      (best, item) =>
        !best || item.average < best.average ? item : best,
      null
    );

    return { latest, latestYoY, highest, lowest };
  }, [data, yoyData, seasonalData]);

  if (loading) {
    return <p>Loading seasonal and trend analysis...</p>;
  }

  if (error) {
    return <p style={{ color: "#dc2626" }}>Error: {error}</p>;
  }

  if (!summary) {
    return <p>No remittance records available.</p>;
  }

  return (
    <div style={{ padding: "8px 0 32px" }}>
      <h1 style={{ marginBottom: "8px", color: "#0f172a" }}>
        Seasonal &amp; Trend Analysis
      </h1>

      <p style={{ color: "#64748b", marginBottom: "24px" }}>
        Explore historical Philippine cash remittance trends,
        seasonal patterns, and year-over-year changes.
      </p>

      {/* Summary Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(210px, 1fr))",
          gap: "16px",
        }}
      >
        <div style={cardStyle}>
          <p style={{ color: "#64748b" }}>Historical Records</p>
          <h2>{data.length} Months</h2>
        </div>

        <div style={cardStyle}>
          <p style={{ color: "#64748b" }}>Latest Remittance</p>
          <h2>${formatMoney(summary.latest.cash)}M</h2>
          <small>{summary.latest.month}</small>
        </div>

        <div style={cardStyle}>
          <p style={{ color: "#64748b" }}>Latest YoY Growth</p>
          <h2
            style={{
              color:
                summary.latestYoY !== null &&
                summary.latestYoY >= 0
                  ? "#16a34a"
                  : "#dc2626",
            }}
          >
            {formatPercent(summary.latestYoY)}
          </h2>
        </div>

        <div style={cardStyle}>
          <p style={{ color: "#64748b" }}>
            Highest Seasonal Average
          </p>
          <h2>{summary.highest?.month || "N/A"}</h2>
          <small>
            {summary.highest
              ? `$${formatMoney(summary.highest.average)}M`
              : "N/A"}
          </small>
        </div>
      </div>

      {/* Historical Trend */}
      <section style={sectionStyle}>
        <h2>Historical Remittance Trend</h2>
        <p style={{ color: "#64748b" }}>
          Monthly cash remittances in million USD.
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
                  `$${formatMoney(value)}M`,
                  "Cash Remittances",
                ]}
              />
              <Line
                type="monotone"
                dataKey="cash"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
                name="Cash Remittances"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Seasonal Averages */}
      <section style={sectionStyle}>
        <h2>Average Monthly Remittances</h2>
        <p style={{ color: "#64748b" }}>
          Historical average for each calendar month.
          These are descriptive averages, not forecasts.
        </p>

        <div style={{ width: "100%", height: 340 }}>
          <ResponsiveContainer>
            <BarChart data={seasonalData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip
                formatter={(value) => [
                  `$${formatMoney(value)}M`,
                  "Average Remittances",
                ]}
              />
              <Bar
                dataKey="average"
                fill="#2563eb"
                radius={[5, 5, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* YoY Growth */}
      <section style={sectionStyle}>
        <h2>Year-over-Year Remittance Growth</h2>
        <p style={{ color: "#64748b" }}>
          Percentage change compared with the same month
          in the previous year.
        </p>

        <div style={{ width: "100%", height: 340 }}>
          <ResponsiveContainer>
            <LineChart data={yoyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                minTickGap={35}
                tick={{ fontSize: 11 }}
              />
              <YAxis tickFormatter={(value) => `${value}%`} />
              <Tooltip
                formatter={(value) => [
                  `${Number(value).toFixed(2)}%`,
                  "YoY Growth",
                ]}
              />
              <Line
                type="monotone"
                dataKey="yoy"
                stroke="#16a34a"
                strokeWidth={2}
                dot={false}
                connectNulls={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Yearly Comparison */}
      <section style={sectionStyle}>
        <h2>Monthly Comparison Across Years</h2>
        <p style={{ color: "#64748b" }}>
          Compare how remittances change across calendar
          months in different years.
        </p>

        <div style={{ width: "100%", height: 380 }}>
          <ResponsiveContainer>
            <LineChart data={yearlyComparison}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip
                formatter={(value) => `$${formatMoney(value)}M`}
              />
              <Legend />
              {years.map((year, index) => {
                const colors = [
                  "#2563eb",
                  "#16a34a",
                  "#f59e0b",
                  "#8b5cf6",
                  "#ef4444",
                  "#0891b2",
                  "#64748b",
                  "#db2777",
                ];

                return (
                  <Line
                    key={year}
                    type="monotone"
                    dataKey={year}
                    name={year}
                    stroke={colors[index % colors.length]}
                    strokeWidth={2}
                    connectNulls={false}
                  />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Interpretation */}
      <section style={sectionStyle}>
        <h2>Key Insights</h2>

        <p>
          <strong>Historical coverage:</strong> The dataset
          contains {data.length} monthly observations from{" "}
          {data[0].month} to {summary.latest.month}.
        </p>

        <p>
          <strong>Seasonal pattern:</strong> Based on the
          available historical observations,{" "}
          {summary.highest?.month} has the highest average
          remittances, while {summary.lowest?.month} has
          the lowest average.
        </p>

        <p>
          <strong>Latest year-over-year change:</strong>{" "}
          {formatPercent(summary.latestYoY)} compared with
          the same month of the previous year.
        </p>

        <p style={{ color: "#64748b" }}>
          Note: These charts describe historical patterns
          and do not establish economic causation.
          Some recent observations may be preliminary.
          The final year may contain fewer than 12 months.
        </p>
      </section>
    </div>
  );
}

export default SeasonalAnalysis;
