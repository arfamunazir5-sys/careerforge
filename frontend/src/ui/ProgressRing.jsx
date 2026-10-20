import "../theme.css";
import "./Ring.css";

export default function ProgressRing({
  value,
  size = 120,
  stroke = 12,
  color = "var(--cf-primary)",
  label,
  sublabel,
}) {
  const v = Math.max(0, Math.min(100, Number(value) || 0));
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - v / 100);
  const center = size / 2;
  const shown = label ?? Math.round(v);

  return (
    <div
      className="ring-wrap"
      style={{ width: size, height: size }}
      role="img"
      aria-label={`${shown} ${sublabel || ""}`.trim()}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={center} cy={center} r={r} fill="none" stroke="var(--cf-border)" strokeWidth={stroke} />
        <circle
          className="ring-arc"
          cx={center}
          cy={center}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${center} ${center})`}
        />
      </svg>
      <div className="ring-center">
        <span className="ring-value">{shown}</span>
        {sublabel && <span className="ring-sub">{sublabel}</span>}
      </div>
    </div>
  );
}