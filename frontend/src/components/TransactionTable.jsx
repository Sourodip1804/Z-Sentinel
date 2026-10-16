export default function TransactionTable({
  transactions = [],
  total = 0,
  page,
  pageSize,
  loading,
  error,
  riskFilter,
  decisionFilter,
  onRiskFilter,
  onDecisionFilter,
  onPageChange,
  onSelect,
}) {
  return (
    <section className="panel">
      <div className="table-header">
        <h2>Transaction history</h2>
        <div className="filters">
          <select value={riskFilter} onChange={(event) => onRiskFilter(event.target.value)}>
            <option value="">All risk levels</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
          </select>
          <select
            value={decisionFilter}
            onChange={(event) => onDecisionFilter(event.target.value)}
          >
            <option value="">All decisions</option>
            <option value="APPROVE">APPROVE</option>
            <option value="REVIEW">REVIEW</option>
            <option value="BLOCK">BLOCK</option>
          </select>
        </div>
      </div>
      {loading ? <p className="muted">Loading transactions…</p> : null}
      {error ? <p className="form-error">{error}</p> : null}
      {!loading && !error && transactions.length === 0 ? (
        <p className="muted">No transactions match the current filters.</p>
      ) : null}
      {!loading && transactions.length > 0 ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>Source</th>
                <th>Amount</th>
                <th>Risk level</th>
                <th>Risk score</th>
                <th>Decision</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.transaction_id} onClick={() => onSelect?.(tx)}>
                  <td>{tx.transaction_id}</td>
                  <td>{tx.source}</td>
                  <td>
                    {tx.currency} {Number(tx.amount || 0).toLocaleString()}
                  </td>
                  <td>
                    <span className={`badge ${String(tx.risk_level).toLowerCase()}`}>
                      {tx.risk_level}
                    </span>
                  </td>
                  <td>{tx.risk_score}</td>
                  <td>{tx.decision}</td>
                  <td>{tx.timestamp ? new Date(tx.timestamp).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      <div className="pagination">
        <button
          type="button"
          disabled={page <= 1 || loading}
          onClick={() => onPageChange(page - 1)}
        >
          Previous
        </button>
        <span>
          Page {page} · {total} total
        </span>
        <button
          type="button"
          disabled={page * pageSize >= total || loading}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </button>
      </div>
    </section>
  );
}
