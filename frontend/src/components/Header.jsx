export default function Header({
  online,
  onSimulate,
  loading,
  scenario,
  onScenarioChange,
  isStreaming,
  onToggleStreaming,
}) {
  return (
    <header className="header">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">
          Z
        </span>
        <div>
          <h1>Z-SENTINEL</h1>
          <p>Real-Time AI Fraud Risk &amp; Decision Engine</p>
        </div>
      </div>
      <div className="header-actions">
        <span className={online ? "status online" : "status offline"}>
          <span className="dot" />
          {online ? "Backend online" : "Backend offline"}
        </span>

        <div className="simulator-controls">
          <select
            className="scenario-select"
            value={scenario}
            onChange={(e) => onScenarioChange(e.target.value)}
            disabled={loading || isStreaming}
          >
            <option value="">Random Scenario</option>
            <option value="high_amount_online">High Amount (Online)</option>
            <option value="legitimate_grocery">Legitimate Grocery</option>
            <option value="new_device_travel">New Device Travel</option>
            <option value="night_velocity">Night Velocity Spike</option>
            <option value="location_spike">Location Deviation Spike</option>
          </select>

          <button
            className="primary-btn"
            type="button"
            onClick={() => onSimulate()}
            disabled={loading || isStreaming}
          >
            {loading && !isStreaming ? "Scoring…" : "Simulate"}
          </button>

          <button
            className={`stream-btn ${isStreaming ? "active" : ""}`}
            type="button"
            onClick={onToggleStreaming}
            title={isStreaming ? "Pause real-time continuous stream" : "Start continuous real-time transaction simulation"}
          >
            {isStreaming ? "⏸ Pause Stream" : "▶ Auto-Stream"}
          </button>
        </div>
      </div>
    </header>
  );
}
