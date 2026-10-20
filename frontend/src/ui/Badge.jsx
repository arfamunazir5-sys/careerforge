import "../theme.css";
import { agentMeta } from "./agentMeta";
import { AgentIcon } from "./agentIcons";

// <Badge tone="success">Done</Badge>   or   <Badge agent="networking" />
export default function Badge({ tone = "neutral", agent, children }) {
  if (agent) {
    const meta = agentMeta(agent);
    return (
      <span className="cf-badge">
        <span style={{ color: meta.color, display: "inline-flex" }}>
          <AgentIcon agent={agent} size={12} />
        </span>
        {children || meta.label}
      </span>
    );
  }
  const toneClass = tone === "neutral" ? "" : ` cf-badge-${tone}`;
  return <span className={`cf-badge${toneClass}`}>{children}</span>;
}