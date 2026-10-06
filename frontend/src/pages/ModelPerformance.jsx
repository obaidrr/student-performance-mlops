import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

function MetricCard({ label, value, unit = "", color = "#4f46e5" }) {
  return (
    <div style={s.metricCard}>
      <span style={s.metricLabel}>{label}</span>
      <span style={{ ...s.metricValue, color }}>{typeof value === "number" ? value.toFixed(4) : value ?? "—"}{unit}</span>
    </div>
  );
}

function ModelRow({ name, metrics, isChampion }) {
  const r2Pct = metrics?.r2 != null ? (metrics.r2 * 100).toFixed(1) : "—";
  return (
    <tr style={isChampion ? s.trChampion : s.tr}>
      <td style={s.td}>
        <span style={s.modelName}>{name}</span>
        {isChampion && <span style={s.champion}>Champion</span>}
      </td>
      <td style={s.tdNum}>{metrics?.r2?.toFixed(4) ?? "—"}</td>
      <td style={s.tdNum}>{metrics?.rmse?.toFixed(4) ?? "—"}</td>
      <td style={s.tdNum}>{metrics?.mae?.toFixed(4) ?? "—"}</td>
      <td style={s.tdNum}>{metrics?.explained_variance?.toFixed(4) ?? "—"}</td>
      <td style={s.tdNum}>
        <div style={s.barWrapper}>
          <div style={{ ...s.barFill, width: `${Math.max(0, parseFloat(r2Pct))}%`, background: isChampion ? "#4f46e5" : "#334155" }} />
          <span style={s.barLabel}>{r2Pct}%</span>
        </div>
      </td>
    </tr>
  );
}

export default function ModelPerformance() {
  const [data, setData] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [perfRes, compRes] = await Promise.allSettled([
          axios.get(`${API_BASE}/model-performance`),
          axios.get(`${API_BASE}/model-performance/comparison`),
        ]);
        if (perfRes.status === "fulfilled") setData(perfRes.value.data);
        else setError(perfRes.reason.response?.data?.detail || "Failed to load metrics");
        if (compRes.status === "fulfilled") setComparison(compRes.value.data);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const allModels = data?.all_models ?? {};
  const champion = data?.champion_model ?? "";

  const barData = Object.entries(allModels).map(([name, m]) => ({
    name: name.replace("_trained", "").replace("_tuned", "").replace("_baseline", ""),
    R2: parseFloat((m.r2 ?? 0).toFixed(4)),
    RMSE: parseFloat((m.rmse ?? 0).toFixed(4)),
    MAE: parseFloat((m.mae ?? 0).toFixed(4)),
  }));

  const radarData = champion && allModels[champion]
    ? [
        { metric: "R²", value: (allModels[champion].r2 ?? 0) * 100 },
        { metric: "Expl. Var", value: (allModels[champion].explained_variance ?? 0) * 100 },
        { metric: "Acc (100-RMSE)", value: Math.max(0, 100 - (allModels[champion].rmse ?? 100)) },
        { metric: "Prec (100-MAE)", value: Math.max(0, 100 - (allModels[champion].mae ?? 100)) },
      ]
    : [];

  const selectionResults = comparison?.results ?? [];

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>Model Performance</h1>
        <p style={s.subtitle}>Evaluation metrics for all trained and tuned models in the ML pipeline.</p>
      </div>

      {loading && <div style={s.center}><span style={s.spinner}>⏳</span> Loading metrics...</div>}

      {error && (
        <div style={s.errorBox}>
          <strong>Error:</strong> {error}
          <p style={{ marginTop: "8px", fontSize: "13px" }}>
            Run the Airflow ML pipeline to generate model metrics.
          </p>
        </div>
      )}

      {!loading && !error && data && (
        <>
          {/* Champion metrics */}
          {champion && allModels[champion] && (
            <div style={s.card}>
              <div style={s.cardHeader}>
                <h2 style={s.cardTitle}>Champion Model</h2>
                <span style={s.championBadge}>{champion}</span>
              </div>
              <div style={s.metricsRow}>
                <MetricCard label="R² Score" value={allModels[champion].r2} color="#4f46e5" />
                <MetricCard label="RMSE" value={allModels[champion].rmse} color="#ef4444" />
                <MetricCard label="MAE" value={allModels[champion].mae} color="#f59e0b" />
                <MetricCard label="Explained Variance" value={allModels[champion].explained_variance} color="#22c55e" />
                <MetricCard label="Max Error" value={allModels[champion].max_error} color="#06b6d4" />
              </div>
            </div>
          )}

          {/* R2 Bar Chart */}
          {barData.length > 0 && (
            <div style={s.card}>
              <h2 style={s.cardTitle}>R² Score Comparison</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={barData} margin={{ top: 10, right: 30, left: 0, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} angle={-30} textAnchor="end" />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} domain={[0, 1]} />
                  <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "#f1f5f9" }} />
                  <Legend wrapperStyle={{ color: "#94a3b8" }} />
                  <Bar dataKey="R2" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* RMSE / MAE chart */}
          {barData.length > 0 && (
            <div style={s.card}>
              <h2 style={s.cardTitle}>RMSE & MAE Comparison (lower is better)</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={barData} margin={{ top: 10, right: 30, left: 0, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} angle={-30} textAnchor="end" />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} />
                  <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "#f1f5f9" }} />
                  <Legend wrapperStyle={{ color: "#94a3b8" }} />
                  <Bar dataKey="RMSE" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="MAE" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Radar */}
          {radarData.length > 0 && (
            <div style={s.card}>
              <h2 style={s.cardTitle}>Champion Model — Performance Radar</h2>
              <ResponsiveContainer width="100%" height={320}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="metric" tick={{ fill: "#94a3b8", fontSize: 13 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 11 }} />
                  <Radar dataKey="value" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.3} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Full metrics table */}
          {Object.keys(allModels).length > 0 && (
            <div style={s.card}>
              <h2 style={s.cardTitle}>All Models — Detailed Metrics</h2>
              <div style={{ overflowX: "auto" }}>
                <table style={s.table}>
                  <thead>
                    <tr>
                      {["Model", "R²", "RMSE", "MAE", "Explained Variance", "R² Visualized"].map((h) => (
                        <th key={h} style={s.th}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(allModels)
                      .sort((a, b) => (b[1].r2 ?? 0) - (a[1].r2 ?? 0))
                      .map(([name, metrics]) => (
                        <ModelRow key={name} name={name} metrics={metrics} isChampion={name === champion} />
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Selection phase comparison */}
          {selectionResults.length > 0 && (
            <div style={s.card}>
              <h2 style={s.cardTitle}>Model Selection Phase — Benchmarks</h2>
              <div style={{ overflowX: "auto" }}>
                <table style={s.table}>
                  <thead>
                    <tr>
                      {["Rank", "Model", "R²", "RMSE", "MAE", "CV R² (mean±std)"].map((h) => (
                        <th key={h} style={s.th}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {selectionResults.map((r, i) => (
                      <tr key={r.model} style={s.tr}>
                        <td style={s.td}>{i + 1}</td>
                        <td style={s.td}>{r.model}</td>
                        <td style={s.tdNum}>{r.r2.toFixed(4)}</td>
                        <td style={s.tdNum}>{r.rmse.toFixed(4)}</td>
                        <td style={s.tdNum}>{r.mae.toFixed(4)}</td>
                        <td style={s.tdNum}>{r.cv_r2_mean.toFixed(4)} ± {r.cv_r2_std.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

const s = {
  page: { maxWidth: "1200px", margin: "0 auto", padding: "40px 2rem" },
  header: { marginBottom: "36px" },
  title: { fontSize: "2rem", fontWeight: "700", color: "#f1f5f9", marginBottom: "8px" },
  subtitle: { color: "#64748b" },
  center: { textAlign: "center", padding: "60px", color: "#64748b", fontSize: "16px" },
  spinner: { fontSize: "1.5rem" },
  errorBox: {
    background: "rgba(239,68,68,0.1)",
    border: "1px solid rgba(239,68,68,0.3)",
    borderRadius: "12px",
    padding: "24px",
    color: "#fca5a5",
  },
  card: {
    background: "#1e293b",
    borderRadius: "12px",
    border: "1px solid #334155",
    padding: "28px",
    marginBottom: "24px",
  },
  cardHeader: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "24px" },
  cardTitle: { fontSize: "16px", fontWeight: "700", color: "#f1f5f9", marginBottom: "20px" },
  championBadge: {
    padding: "4px 12px",
    background: "rgba(79, 70, 229, 0.2)",
    border: "1px solid rgba(79, 70, 229, 0.4)",
    borderRadius: "20px",
    fontSize: "12px",
    color: "#818cf8",
    fontWeight: "600",
  },
  metricsRow: { display: "flex", gap: "16px", flexWrap: "wrap" },
  metricCard: {
    flex: "1 1 140px",
    background: "#0f172a",
    borderRadius: "8px",
    padding: "16px",
    display: "flex",
    flexDirection: "column",
    gap: "6px",
  },
  metricLabel: { fontSize: "11px", color: "#64748b", fontWeight: "600", textTransform: "uppercase", letterSpacing: "0.05em" },
  metricValue: { fontSize: "1.5rem", fontWeight: "800" },
  table: { width: "100%", borderCollapse: "collapse" },
  th: {
    padding: "10px 14px",
    textAlign: "left",
    fontSize: "11px",
    color: "#64748b",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    borderBottom: "1px solid #334155",
  },
  tr: { borderBottom: "1px solid #1e293b" },
  trChampion: { borderBottom: "1px solid #1e293b", background: "rgba(79,70,229,0.08)" },
  td: { padding: "12px 14px", fontSize: "14px", color: "#f1f5f9" },
  tdNum: { padding: "12px 14px", fontSize: "14px", color: "#cbd5e1", fontVariantNumeric: "tabular-nums" },
  modelName: { fontWeight: "600" },
  champion: {
    marginLeft: "8px",
    padding: "2px 8px",
    background: "rgba(79, 70, 229, 0.2)",
    border: "1px solid rgba(79, 70, 229, 0.4)",
    borderRadius: "10px",
    fontSize: "11px",
    color: "#818cf8",
    fontWeight: "600",
  },
  barWrapper: { display: "flex", alignItems: "center", gap: "8px", width: "120px" },
  barFill: { height: "8px", borderRadius: "4px", minWidth: "2px", transition: "width 0.3s" },
  barLabel: { fontSize: "12px", color: "#94a3b8", whiteSpace: "nowrap" },
};
