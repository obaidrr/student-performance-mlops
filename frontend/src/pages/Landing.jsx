import React from "react";
import { Link } from "react-router-dom";

const features = [
  {
    icon: "🧠",
    title: "ML-Powered Predictions",
    desc: "Trained on 6,000+ student records using Gradient Boosting and Random Forest models.",
  },
  {
    icon: "⚙️",
    title: "End-to-End Pipeline",
    desc: "Automated Airflow pipeline handles preprocessing, training, tuning, and extraction.",
  },
  {
    icon: "📊",
    title: "Rich Analytics",
    desc: "Compare model performance metrics including RMSE, MAE, and R² scores.",
  },
  {
    icon: "🚀",
    title: "FastAPI Backend",
    desc: "High-performance REST API with real-time prediction capabilities.",
  },
  {
    icon: "🗄️",
    title: "MySQL Data Store",
    desc: "Preprocessed dataset stored and queried from a production-grade MySQL database.",
  },
  {
    icon: "🐳",
    title: "Docker Compose",
    desc: "Fully containerized services for easy deployment and reproducibility.",
  },
];

const pipeline = [
  { step: "01", title: "Preprocess & Ingest", desc: "Clean CSV data and load into MySQL" },
  { step: "02", title: "Model Selection", desc: "Benchmark 8 regression models" },
  { step: "03", title: "Model Training", desc: "Train top-3 models on full dataset" },
  { step: "04", title: "Hyperparameter Tuning", desc: "RandomizedSearchCV optimization" },
  { step: "05", title: "Model Testing", desc: "Comprehensive evaluation & sanity checks" },
  { step: "06", title: "Model Extraction", desc: "Export champions as joblib artifacts" },
];

export default function Landing() {
  return (
    <div style={s.page}>
      {/* Hero */}
      <section style={s.hero}>
        <div style={s.heroInner}>
          <div style={s.badge}>Student Performance ML Pipeline</div>
          <h1 style={s.heroTitle}>
            Predict Student{" "}
            <span style={s.heroGradient}>Exam Scores</span>
            <br />
            with Machine Learning
          </h1>
          <p style={s.heroSubtitle}>
            An end-to-end MLOps pipeline built with Apache Airflow, scikit-learn,
            FastAPI, and React. Input student factors and get instant exam score predictions.
          </p>
          <div style={s.heroCta}>
            <Link to="/predict" style={s.ctaPrimary}>Make a Prediction</Link>
            <Link to="/performance" style={s.ctaSecondary}>View Model Performance</Link>
          </div>
        </div>

        <div style={s.statsRow}>
          {[
            { value: "6,607", label: "Training Samples" },
            { value: "19", label: "Input Features" },
            { value: "8", label: "Models Evaluated" },
            { value: "6", label: "Airflow DAGs" },
          ].map((stat) => (
            <div key={stat.label} style={s.statCard}>
              <span style={s.statValue}>{stat.value}</span>
              <span style={s.statLabel}>{stat.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Pipeline Steps */}
      <section style={s.section}>
        <h2 style={s.sectionTitle}>ML Pipeline Overview</h2>
        <p style={s.sectionSubtitle}>6 Airflow DAGs orchestrate the full machine learning workflow</p>
        <div style={s.pipelineGrid}>
          {pipeline.map((p, i) => (
            <div key={p.step} style={s.pipelineCard}>
              <div style={s.pipelineStep}>{p.step}</div>
              <div style={s.pipelineConnector} hidden={i === pipeline.length - 1} />
              <h3 style={s.pipelineTitle}>{p.title}</h3>
              <p style={s.pipelineDesc}>{p.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section style={{ ...s.section, background: "#1e293b" }}>
        <h2 style={s.sectionTitle}>Features</h2>
        <div style={s.featuresGrid}>
          {features.map((f) => (
            <div key={f.title} style={s.featureCard}>
              <span style={s.featureIcon}>{f.icon}</span>
              <h3 style={s.featureTitle}>{f.title}</h3>
              <p style={s.featureDesc}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={s.ctaSection}>
        <h2 style={s.ctaTitle}>Ready to predict?</h2>
        <p style={s.ctaSubtitle}>Enter student information and get an instant exam score prediction.</p>
        <Link to="/predict" style={s.ctaPrimary}>Get Started</Link>
      </section>
    </div>
  );
}

const s = {
  page: { width: "100%" },
  hero: {
    padding: "80px 2rem 60px",
    textAlign: "center",
    background: "linear-gradient(180deg, #0f172a 0%, #1e293b 100%)",
    borderBottom: "1px solid #334155",
  },
  heroInner: { maxWidth: "800px", margin: "0 auto" },
  badge: {
    display: "inline-block",
    padding: "4px 12px",
    background: "rgba(79, 70, 229, 0.2)",
    border: "1px solid rgba(79, 70, 229, 0.4)",
    borderRadius: "20px",
    fontSize: "12px",
    color: "#818cf8",
    fontWeight: "600",
    letterSpacing: "0.05em",
    textTransform: "uppercase",
    marginBottom: "24px",
  },
  heroTitle: {
    fontSize: "clamp(2rem, 5vw, 3.5rem)",
    fontWeight: "800",
    lineHeight: "1.15",
    color: "#f1f5f9",
    marginBottom: "20px",
  },
  heroGradient: {
    background: "linear-gradient(90deg, #4f46e5, #06b6d4)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
  },
  heroSubtitle: {
    fontSize: "1.1rem",
    color: "#94a3b8",
    maxWidth: "600px",
    margin: "0 auto 36px",
  },
  heroCta: {
    display: "flex",
    gap: "12px",
    justifyContent: "center",
    flexWrap: "wrap",
    marginBottom: "60px",
  },
  ctaPrimary: {
    padding: "12px 28px",
    background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
    color: "#fff",
    borderRadius: "8px",
    fontWeight: "600",
    fontSize: "15px",
    border: "none",
    display: "inline-block",
  },
  ctaSecondary: {
    padding: "12px 28px",
    background: "transparent",
    color: "#94a3b8",
    borderRadius: "8px",
    fontWeight: "600",
    fontSize: "15px",
    border: "1px solid #334155",
    display: "inline-block",
  },
  statsRow: {
    display: "flex",
    justifyContent: "center",
    gap: "24px",
    flexWrap: "wrap",
    maxWidth: "800px",
    margin: "0 auto",
  },
  statCard: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "20px 32px",
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "12px",
    minWidth: "140px",
  },
  statValue: {
    fontSize: "2rem",
    fontWeight: "800",
    background: "linear-gradient(90deg, #4f46e5, #06b6d4)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
  },
  statLabel: { color: "#64748b", fontSize: "13px", marginTop: "4px" },
  section: { padding: "80px 2rem" },
  sectionTitle: {
    textAlign: "center",
    fontSize: "2rem",
    fontWeight: "700",
    color: "#f1f5f9",
    marginBottom: "12px",
  },
  sectionSubtitle: {
    textAlign: "center",
    color: "#64748b",
    marginBottom: "48px",
  },
  pipelineGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "20px",
    maxWidth: "1100px",
    margin: "0 auto",
  },
  pipelineCard: {
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "12px",
    padding: "24px",
    position: "relative",
    overflow: "hidden",
  },
  pipelineStep: {
    fontSize: "2.5rem",
    fontWeight: "900",
    background: "linear-gradient(135deg, #4f46e5, #06b6d4)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
    lineHeight: "1",
    marginBottom: "12px",
  },
  pipelineConnector: {},
  pipelineTitle: {
    fontSize: "16px",
    fontWeight: "700",
    color: "#f1f5f9",
    marginBottom: "6px",
  },
  pipelineDesc: { fontSize: "13px", color: "#64748b" },
  featuresGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "20px",
    maxWidth: "1100px",
    margin: "0 auto",
  },
  featureCard: {
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: "12px",
    padding: "24px",
  },
  featureIcon: { fontSize: "2rem", marginBottom: "12px", display: "block" },
  featureTitle: { fontSize: "16px", fontWeight: "700", color: "#f1f5f9", marginBottom: "8px" },
  featureDesc: { fontSize: "14px", color: "#64748b", lineHeight: "1.5" },
  ctaSection: {
    textAlign: "center",
    padding: "80px 2rem",
    background: "linear-gradient(180deg, #1e293b 0%, #0f172a 100%)",
    borderTop: "1px solid #334155",
  },
  ctaTitle: { fontSize: "2rem", fontWeight: "700", color: "#f1f5f9", marginBottom: "12px" },
  ctaSubtitle: { color: "#64748b", marginBottom: "32px" },
};
