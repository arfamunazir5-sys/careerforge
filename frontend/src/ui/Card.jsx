import "../theme.css";

export default function Card({ title, subtitle, action, accent, className = "", children }) {
  const style = accent ? { borderTop: `3px solid ${accent}` } : undefined;
  return (
    <section className={`cf-card ${className}`.trim()} style={style}>
      {(title || action) && (
        <header className="cf-card-head">
          <div>
            {title && <h3 className="cf-card-title">{title}</h3>}
            {subtitle && <p className="cf-card-subtitle">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </header>
      )}
      <div>{children}</div>
    </section>
  );
}