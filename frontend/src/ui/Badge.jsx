import "../theme.css";
import { agentMeta } from "./agentMeta";

// <Badge tone="success">Done</Badge>   or   <Badge agent="networking" />
export default function Badge({ tone = "neutral", agent, children }) {
  if (agent) {
    const meta = agentMeta(agent);
    return (
      <span className="cf-badge">
        <span className="cf-badge-dot" style={{ background: meta.color }} />
        {children || meta.label}
      </span>
    );
  }
  const toneClass = tone === "neutral" ? "" : ` cf-badge-${tone}`;
  return <span className={`cf-badge${toneClass}`}>{children}</span>;
}