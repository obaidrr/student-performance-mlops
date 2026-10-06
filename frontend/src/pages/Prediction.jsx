import React, { useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

const FIELDS = [
  { key: "hours_studied", label: "Hours Studied per Day", type: "number", min: 0, max: 24, step: 0.5, default: 6 },
  { key: "attendance", label: "Attendance (%)", type: "number", min: 0, max: 100, step: 1, default: 85 },
  { key: "previous_scores", label: "Previous Scores (0-100)", type: "number", min: 0, max: 100, step: 1, default: 70 },
  { key: "sleep_hours", label: "Sleep Hours per Day", type: "number", min: 0, max: 24, step: 0.5, default: 7 },
  { key: "tutoring_sessions", label: "Tutoring Sessions", type: "number", min: 0, max: 20, step: 1, default: 1 },
  { key: "physical_activity", label: "Physical Activity (hrs/week)", type: "number", min: 0, max: 50, step: 1, default: 3 },
  { key: "parental_involvement", label: "Parental Involvement", type: "select", options: ["Low", "Medium", "High"], default: "Medium" },
  { key: "access_to_resources", label: "Access to Resources", type: "select", options: ["Low", "Medium", "High"], default: "Medium" },
  { key: "extracurricular_activities", label: "Extracurricular Activities", type: "select", options: ["Yes", "No"], default: "No" },
  { key: "motivation_level", label: "Motivation Level", type: "select", options: ["Low", "Medium", "High"], default: "Medium" },
  { key: "internet_access", label: "Internet Access", type: "select", options: ["Yes", "No"], default: "Yes" },
  { key: "family_income", label: "Family Income", type: "select", options: ["Low", "Medium", "High"], default: "Medium" },
  { key: "teacher_quality", label: "Teacher Quality", type: "select", options: ["Low", "Medium", "High"], default: "Medium" },
  { key: "school_type", label: "School Type", type: "select", options: ["Public", "Private"], default: "Public" },
  { key: "peer_influence", label: "Peer Influence", type: "select", options: ["Negative", "Neutral", "Positive"], default: "Neutral" },
  { key: "learning_disabilities", label: "Learning Disabilities", type: "select", options: ["Yes", "No"], default: "No" },
  { key: "parental_education_level", label: "Parental Education Level", type: "select", options: ["High School", "College", "Postgraduate"], default: "College" },
  { key: "distance_from_home", label: "Distance from Home", type: "select", options: ["Near", "Moderate", "Far"], default: "Near" },
  { key: "gender", label: "Gender", type: "select", options: ["Male", "Female"], default: "Male" },
];

function getInitialForm() {
  return Object.fromEntries(FIELDS.map((f) => [f.key, f.default]));
}

function ScoreGauge({ score }) {
  const pct = Math.min(100, Math.max(0, score));
  const color = pct >= 75 ? "#22c55e" : pct >= 55 ? "#f59e0b" : "#ef4444";
  const label = pct >= 75 ? "Excellent" : pct >= 60 ? "Good" : pct >= 45 ? "Average" : "Below Average";
  return (
    <div style={gs.wrapper}>
      <svg width="180" height="100" viewBox="0 0 180 100">
        <path d="M 20 90 A 70 70 0 0 1 160 90" fill="none" stroke="#334155" strokeWidth="14" strokeLinecap="round" />
        <path
          d="M 20 90 A 70 70 0 0 1 160 90"
          fill="none"
          stroke={color}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={`${(pct / 100) * 220} 220`}
        />
      </svg>
      <div style={{ ...gs.scoreText, color }}>
        <span style={gs.scoreNum}>{pct.toFixed(1)}</span>
        <span style={gs.scoreMax}>/100</span>
      </div>
      <div style={{ ...gs.scoreLabel, color }}>{label}</div>
    </div>
  );
}

const gs = {
  wrapper: { display: "flex", flexDirection: "column", alignItems: "center", position: "relative" },
  scoreText: { position: "absolute", top: "42px", textAlign: "center" },
  scoreNum: { fontSize: "2.2rem", fontWeight: "800" },
  scoreMax: { fontSize: "1rem", color: "#64748b", marginLeft: "2px" },
  scoreLabel: { fontSize: "14px", fontWeight: "600", marginTop: "8px" },
};

export default function Prediction() {
  const [form, setForm] = useState(getInitialForm);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (key, value) => {
    const field = FIELDS.find((f) => f.key === key);
    setForm((prev) => ({
      ...prev,
      [key]: field?.type === "number" ? parseFloat(value) || 0 : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const payload = { ...form };
      const res = await axios.post(`${API_BASE}/predict`, payload);
      setResult(res.data);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || "Prediction failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setForm(getInitialForm());
    setResult(null);
    setError(null);
  };

  const numerics = FIELDS.filter((f) => f.type === "number");
  const selects = FIELDS.filter((f) => f.type === "select");

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>Make a Prediction</h1>
        <p style={s.subtitle}>Fill in student information to predict the exam score.</p>
      </div>

      <div style={s.layout}>
        <form onSubmit={handleSubmit} style={s.form}>
          <div style={s.section}>
            <h2 style={s.sectionTitle}>Numeric Features</h2>
            <div style={s.grid}>
              {numerics.map((f) => (
                <div key={f.key} style={s.field}>
                  <label style={s.label}>{f.label}</label>
                  <input
                    type="number"
                    min={f.min}
                    max={f.max}
                    step={f.step}
                    value={form[f.key]}
                    onChange={(e) => handleChange(f.key, e.target.value)}
                    style={s.input}
                    required
                  />
                </div>
              ))}
            </div>
          </div>

          <div style={s.section}>
            <h2 style={s.sectionTitle}>Categorical Features</h2>
            <div style={s.grid}>
              {selects.map((f) => (
                <div key={f.key} style={s.field}>
                  <label style={s.label}>{f.label}</label>
                  <select
                    value={form[f.key]}
                    onChange={(e) => handleChange(f.key, e.target.value)}
                    style={s.select}
                    required
                  >
                    {f.options.map((o) => (
                      <option key={o} value={o}>{o}</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>

          <div style={s.actions}>
            <button type="submit" style={s.btnPrimary} disabled={loading}>
              {loading ? "Predicting..." : "Predict Exam Score"}
            </button>
            <button type="button" style={s.btnSecondary} onClick={handleReset}>
              Reset
            </button>
          </div>
        </form>

        <div style={s.resultPanel}>
          <h2 style={s.sectionTitle}>Prediction Result</h2>
          {!result && !error && !loading && (
            <div style={s.placeholder}>
              <span style={s.placeholderIcon}>🎯</span>
              <p>Fill in the form and click<br /><strong>Predict Exam Score</strong></p>
            </div>
          )}
          {loading && (
            <div style={s.placeholder}>
              <span style={s.placeholderIcon}>⏳</span>
              <p>Running prediction...</p>
            </div>
          )}
          {error && (
            <div style={s.errorBox}>
              <strong>Error:</strong> {error}
              {typeof error === "string" && error.includes("Model not loaded") && (
                <p style={{ marginTop: "8px", fontSize: "13px" }}>
                  Run the Airflow ML pipeline first to train and extract models.
                </p>
              )}
            </div>
          )}
          {result && (
            <div style={s.resultBox}>
              <ScoreGauge score={result.predicted_exam_score} />
              <div style={s.resultMeta}>
                <div style={s.metaItem}>
                  <span style={s.metaLabel}>Model Used</span>
                  <span style={s.metaValue}>{result.model_used}</span>
                </div>
                <div style={s.metaItem}>
                  <span style={s.metaLabel}>Note</span>
                  <span style={s.metaValue}>{result.confidence_note}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const s = {
  page: { maxWidth: "1200px", margin: "0 auto", padding: "40px 2rem" },
  header: { marginBottom: "36px" },
  title: { fontSize: "2rem", fontWeight: "700", color: "#f1f5f9", marginBottom: "8px" },
  subtitle: { color: "#64748b" },
  layout: { display: "grid", gridTemplateColumns: "1fr 360px", gap: "32px", alignItems: "start" },
  form: { background: "#1e293b", borderRadius: "12px", border: "1px solid #334155", padding: "28px" },
  section: { marginBottom: "28px" },
  sectionTitle: { fontSize: "16px", fontWeight: "700", color: "#94a3b8", marginBottom: "16px", textTransform: "uppercase", letterSpacing: "0.05em" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "16px" },
  field: { display: "flex", flexDirection: "column", gap: "6px" },
  label: { fontSize: "13px", color: "#94a3b8", fontWeight: "500" },
  input: {
    padding: "9px 12px",
    borderRadius: "8px",
    border: "1px solid #334155",
    background: "#0f172a",
    color: "#f1f5f9",
    fontSize: "14px",
    outline: "none",
    width: "100%",
  },
  select: {
    padding: "9px 12px",
    borderRadius: "8px",
    border: "1px solid #334155",
    background: "#0f172a",
    color: "#f1f5f9",
    fontSize: "14px",
    outline: "none",
    width: "100%",
    cursor: "pointer",
  },
  actions: { display: "flex", gap: "12px", paddingTop: "8px" },
  btnPrimary: {
    flex: 1,
    padding: "12px",
    background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontWeight: "600",
    fontSize: "15px",
  },
  btnSecondary: {
    padding: "12px 20px",
    background: "transparent",
    color: "#94a3b8",
    border: "1px solid #334155",
    borderRadius: "8px",
    fontWeight: "600",
    fontSize: "15px",
  },
  resultPanel: {
    background: "#1e293b",
    borderRadius: "12px",
    border: "1px solid #334155",
    padding: "28px",
    position: "sticky",
    top: "80px",
  },
  placeholder: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "40px 20px",
    color: "#475569",
    textAlign: "center",
    gap: "12px",
  },
  placeholderIcon: { fontSize: "2.5rem" },
  errorBox: {
    background: "rgba(239,68,68,0.1)",
    border: "1px solid rgba(239,68,68,0.3)",
    borderRadius: "8px",
    padding: "16px",
    color: "#fca5a5",
    fontSize: "14px",
  },
  resultBox: { display: "flex", flexDirection: "column", gap: "24px", alignItems: "center" },
  resultMeta: { width: "100%", display: "flex", flexDirection: "column", gap: "12px" },
  metaItem: {
    display: "flex",
    justifyContent: "space-between",
    padding: "10px 14px",
    background: "#0f172a",
    borderRadius: "8px",
    gap: "12px",
  },
  metaLabel: { fontSize: "12px", color: "#64748b", fontWeight: "600", textTransform: "uppercase", letterSpacing: "0.05em" },
  metaValue: { fontSize: "13px", color: "#f1f5f9", fontWeight: "500", textAlign: "right", maxWidth: "180px" },
};
