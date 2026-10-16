function factorLabel(factor) {
  const strength = Number(factor.strength || 0).toFixed(3);
  return `${factor.feature}: ${factor.direction.replaceAll("_", " ")} (${strength})`;
}

export default function LatestPrediction({ result, error }) {
  if (error) {
    return (
      <section className="panel">
        <h2>Latest prediction</h2>
        <p className="form-error">{error}</p>
      </section>
    );
  }
  if (!result) {
    return (
      <section className="panel">
        <h2>Latest prediction</h2>
        <p className="muted">
          Submit a transaction or click Simulate Transaction to see a live
          score.
        </p>
      </section>
    );
  }

  const levelClass = String(result.risk_level || "").toLowerCase();

  return (
    <section className="panel">
      <h2>Latest prediction</h2>
      <dl className="result-grid">
        <div>
          <dt>Transaction ID</dt>
          <dd>{result.transaction_id}</dd>
        </div>
        <div>
          <dt>Probability</dt>
          <dd>{(result.fraud_probability * 100).toFixed(2)}%</dd>
        </div>
        <div>
          <dt>Risk score</dt>
          <dd>{result.risk_score}</dd>
        </div>
        <div>
          <dt>Risk level</dt>
          <dd>
            <span className={`badge ${levelClass}`}>{result.risk_level}</span>
          </dd>
        </div>
        <div>
          <dt>Recommended action</dt>
          <dd>{result.decision}</dd>
        </div>
        <div>
          <dt>Model version</dt>
          <dd>{result.model_version}</dd>
        </div>
        <div>
          <dt>Inference latency</dt>
          <dd>{result.inference_time_ms} ms</dd>
        </div>
        <div>
          <dt>Source</dt>
          <dd>{result.source}</dd>
        </div>
      </dl>
      <h3>Explanation factors</h3>
      <ul className="factor-list">
        {(result.top_risk_factors || []).map((factor) => (
          <li key={`${factor.feature}-${factor.contribution}`}>
            {factorLabel(factor)}
            {factor.value != null ? ` · value ${factor.value}` : ""}
          </li>
        ))}
      </ul>
      {result.investigation_summary ? (
        <p className="summary">{result.investigation_summary}</p>
      ) : null}
      <p className="muted">{result.probability_note}</p>
    </section>
  );
}
