import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function VolumeChart({ transactions = [] }) {
  const buckets = new Map();
  for (const tx of transactions) {
    if (!tx.timestamp) continue;
    const key = new Date(tx.timestamp).toISOString().slice(11, 16);
    buckets.set(key, (buckets.get(key) || 0) + 1);
  }
  const data = [...buckets.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([name, value]) => ({ name, value }));

  if (!data.length) {
    return <p className="muted">Volume appears after timestamps are stored.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#29364b" />
        <XAxis dataKey="name" stroke="#94a3b8" />
        <YAxis allowDecimals={false} stroke="#94a3b8" />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#60a5fa" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
