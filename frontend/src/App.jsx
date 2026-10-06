import React from "react";
import { Routes, Route, Link, useLocation } from "react-router-dom";
import Landing from "./pages/Landing";
import Prediction from "./pages/Prediction";
import ModelPerformance from "./pages/ModelPerformance";

function Navbar() {
  const location = useLocation();
  const links = [
    { to: "/", label: "Home" },
    { to: "/predict", label: "Make Prediction" },
    { to: "/performance", label: "Model Performance" },
  ];

  return (
    <nav style={styles.nav}>
      <div style={styles.navBrand}>
        <span style={styles.navLogo}>SP</span>
        <span style={styles.navTitle}>Student Performance Predictor</span>
      </div>
      <div style={styles.navLinks}>
        {links.map((l) => (
          <Link
            key={l.to}
            to={l.to}
            style={{
              ...styles.navLink,
              ...(location.pathname === l.to ? styles.navLinkActive : {}),
            }}
          >
            {l.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <div>
      <Navbar />
      <main style={styles.main}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/predict" element={<Prediction />} />
          <Route path="/performance" element={<ModelPerformance />} />
        </Routes>
      </main>
      <footer style={styles.footer}>
        <p>Student Performance ML Pipeline &mdash; Powered by Airflow, FastAPI &amp; React</p>
      </footer>
    </div>
  );
}

const styles = {
  nav: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 2rem",
    height: "64px",
    background: "#1e293b",
    borderBottom: "1px solid #334155",
    position: "sticky",
    top: 0,
    zIndex: 100,
  },
  navBrand: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  navLogo: {
    width: "36px",
    height: "36px",
    borderRadius: "8px",
    background: "linear-gradient(135deg, #4f46e5, #06b6d4)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "700",
    fontSize: "14px",
    color: "#fff",
    flexShrink: 0,
    lineHeight: "36px",
    textAlign: "center",
  },
  navTitle: {
    fontWeight: "600",
    fontSize: "16px",
    color: "#f1f5f9",
  },
  navLinks: {
    display: "flex",
    gap: "8px",
  },
  navLink: {
    padding: "6px 14px",
    borderRadius: "6px",
    color: "#94a3b8",
    fontSize: "14px",
    fontWeight: "500",
    transition: "all 0.15s",
  },
  navLinkActive: {
    background: "#4f46e5",
    color: "#fff",
  },
  main: {
    minHeight: "calc(100vh - 64px - 56px)",
  },
  footer: {
    textAlign: "center",
    padding: "16px",
    borderTop: "1px solid #334155",
    color: "#64748b",
    fontSize: "13px",
  },
};
