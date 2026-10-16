export default function StatCard({ title, value, hint }) {
  return (
    <article className="stat-card">
      <span className="stat-title">{title}</span>
      <strong>{value}</strong>
      {hint ? <small>{hint}</small> : null}
    </article>
  );
}
