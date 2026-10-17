export const AGENTS = {
  skill_building: { label: "Skill Building", short: "Skills", color: "var(--cf-agent-skill)" },
  networking: { label: "Networking", short: "Network", color: "var(--cf-agent-networking)" },
  portfolio: { label: "Portfolio", short: "Portfolio", color: "var(--cf-agent-portfolio)" },
  interview_prep: { label: "Interview Prep", short: "Interview", color: "var(--cf-agent-interview)" },
};

export function agentMeta(key) {
  return (
    AGENTS[key] || {
      label: String(key || "").replace(/_/g, " "),
      short: String(key || ""),
      color: "var(--cf-text-faint)",
    }
  );
}