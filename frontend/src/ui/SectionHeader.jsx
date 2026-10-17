import "../theme.css";

export default function SectionHeader({ title, subtitle, right }) {
  return (
    <div className="cf-section-header">
      <div>
        <h2 className="cf-section-title">{title}</h2>
        {subtitle && <p className="cf-section-subtitle">{subtitle}</p>}
      </div>
      {right && <div>{right}</div>}
    </div>
  );
}