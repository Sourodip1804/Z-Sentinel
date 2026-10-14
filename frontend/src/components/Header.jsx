export default function Header({ online, onSimulate, loading }) {
  return (
    <header className="header">
      <div className="brand">
        <span className="brand-mark">Z</span>
        <div>
          <h1>Z-SENTINEL</h1>
          <p>Real-Time AI Fraud Risk & Decision Engine</p>
        </div>
      </div>
      <div className="header-actions">
        <span className={online ? "status online" : "status offline"}>
          <span className="dot" />

          {online ? "SYSTEM ONLINE" : "BACKEND OFFLINE"}
        </span>

        <button className="primary-btn" onClick={onSimulate} disabled={loading}>
          {loading ? "ANALYZING..." : "⚡ Simulate Transaction"}
        </button>
      </div>
    </header>
  );
}
