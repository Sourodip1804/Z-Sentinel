import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const COLORS = {
  LOW: "#22c55e",
  MEDIUM: "#f59e0b",
  HIGH: "#ef4444",
};

export default function RiskChart({ risk, loading }) {
  const data = [
    { name: "LOW", value: risk?.LOW || 0 },
    { name: "MEDIUM", value: risk?.MEDIUM || 0 },
    { name: "HIGH", value: risk?.HIGH || 0 },
  ];
  const total = data.reduce((sum, item) => sum + item.value, 0);

  if (loading) {
    return <p className="muted">Loading risk distribution…</p>;
  }
  if (!total) {
    return <p className="muted">No scored transactions yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius={62}
          outerRadius={92}
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
