import { useEffect, useState } from "react";
import { getModelMetrics, getModelStatus } from "../api";

export default function ModelStatus() {
  const [status, setStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [error, setError] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const [statusRes, metricsRes] = await Promise.all([
        getModelStatus(),
        getModelMetrics(),
      ]);
      setStatus(statusRes.data);
      setMetrics(metricsRes.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Could not retrieve model metadata."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let ignore = false;
    async function fetchMetadata() {
      try {
        const [statusRes, metricsRes] = await Promise.all([
          getModelStatus(),
          getModelMetrics(),
        ]);
        if (!ignore) {
          setStatus(statusRes.data);
          setMetrics(metricsRes.data);
          setLoading(false);
        }
      } catch (err) {
        if (!ignore) {
          setError(
            err.response?.data?.detail || "Could not retrieve model metadata."
          );
          setLoading(false);
        }
      }
    }
    fetchMetadata();
    return () => {
      ignore = true;
    };
  }, []);

  const test = metrics?.test_metrics || {};

  return (
    <section className="panel model-panel">
      <div className="panel-header-actions">
        <div>
          <h2>AI Model Pipeline &amp; Evaluation</h2>
          <p className="panel-copy">
            Portable MLz-ready scoring service with calibrated thresholds and feature contract <code>{status?.feature_contract_version || "txn_features_v1"}</code>.
          </p>
        </div>
        <div className="model-actions">
          <button
            type="button"
            className="secondary-btn"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Hide Details" : "View Metrics"}
          </button>
          <button
            type="button"
            className="secondary-btn"
            onClick={loadData}
            disabled={loading}
          >
            {loading ? "…" : "↻"}
          </button>
        </div>
      </div>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="model-summary-grid">
        <div className="meta-item">
          <span className="meta-label">Model Status</span>
          <span className="meta-value">
            {status?.model_ready ? (
              <span className="badge low">Active &amp; Ready</span>
            ) : (
              <span className="badge high">Artifact Missing</span>
            )}
          </span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Model Version</span>
          <span className="meta-value font-mono">
            {status?.model_version || "—"}
          </span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Algorithm</span>
          <span className="meta-value">
            {status?.selected_model
              ? status.selected_model.toUpperCase()
              : "Logistic Regression"}
          </span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Test PR-AUC</span>
          <span className="meta-value highlight">
            {test.pr_auc != null ? test.pr_auc.toFixed(4) : "—"}
          </span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Test ROC-AUC</span>
          <span className="meta-value">
            {test.roc_auc != null ? test.roc_auc.toFixed(4) : "—"}
          </span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Decision Policy</span>
          <span className="meta-value font-mono text-sm">
            Med: {status?.medium_threshold ?? "0.25"} | High:{" "}
            {status?.high_threshold ?? "0.60"}
          </span>
        </div>
      </div>

      {expanded && metrics ? (
        <div className="model-expanded-details">
          <h3>Validation &amp; Test Performance</h3>
          <div className="metrics-detailed-grid">
            <div className="metric-box">
              <span className="box-title">Precision</span>
              <strong>{test.precision != null ? (test.precision * 100).toFixed(1) + "%" : "—"}</strong>
            </div>
            <div className="metric-box">
              <span className="box-title">Recall</span>
              <strong>{test.recall != null ? (test.recall * 100).toFixed(1) + "%" : "—"}</strong>
            </div>
            <div className="metric-box">
              <span className="box-title">F1 Score</span>
              <strong>{test.f1 != null ? test.f1.toFixed(3) : "—"}</strong>
            </div>
            <div className="metric-box">
              <span className="box-title">False Positive Rate</span>
              <strong>{test.false_positive_rate != null ? (test.false_positive_rate * 100).toFixed(2) + "%" : "—"}</strong>
            </div>
          </div>

          {metrics.disclaimer ? (
            <p className="disclaimer-note">
              <strong>Notice:</strong> {metrics.disclaimer}
            </p>
          ) : null}

          {metrics.data_source ? (
            <p className="muted text-xs">
              <strong>Source:</strong> {metrics.data_source}
            </p>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
