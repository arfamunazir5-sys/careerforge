import "../theme.css";

export default function StatCard({ label, value, hint, tone = "neutral" }) {
  return (
    <div className={`cf-stat cf-tone-${tone}`}>
      <div className="cf-stat-label">{label}</div>
      <div className="cf-stat-value">{value}</div>
      {hint && <div className="cf-stat-hint">{hint}</div>}
    </div>
  );
}