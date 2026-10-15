export default function TransactionTable({ transactions = [] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Transaction ID</th>
          <th>Amount</th>
          <th>Fraud probability</th>
          <th>Risk level</th>
          <th>Decision</th>
        </tr>
      </thead>

      <tbody>
        {transactions.map((tx) => (
          <tr key={tx.transaction_id}>
            <td>{tx.transaction_id}</td>
            <td>₹{(tx.amount ?? 0).toLocaleString()}</td>
            <td>{((tx.fraud_probability ?? 0) * 100).toFixed(1)}%</td>
            <td>{tx.risk_level}</td>
            <td>{tx.decision}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}