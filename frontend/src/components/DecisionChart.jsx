import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function DecisionChart({ stats, loading }) {
  const data = [
    { name: "APPROVE", value: stats?.approved || 0, fill: "#22c55e" },
    { name: "REVIEW", value: stats?.review || 0, fill: "#f59e0b" },
    { name: "BLOCK", value: stats?.blocked || 0, fill: "#ef4444" },
  ];
  const total = data.reduce((sum, item) => sum + item.value, 0);

  if (loading) {
    return <p className="muted">Loading decisions…</p>;
  }
  if (!total) {
    return <p className="muted">No decisions recorded yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#29364b" />
        <XAxis dataKey="name" stroke="#94a3b8" />
        <YAxis allowDecimals={false} stroke="#94a3b8" />
        <Tooltip />
        <Bar dataKey="value">
          {data.map((entry) => (
            <Cell key={entry.name} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
