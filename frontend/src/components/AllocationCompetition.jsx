const AGENT_LABELS = {
  skill_building: "Skill Building",
  networking: "Networking",
  portfolio: "Portfolio",
  interview_prep: "Interview Prep",
};

const AGENT_COLORS = {
  skill_building: "var(--agent-skill)",
  networking: "var(--agent-networking)",
  portfolio: "var(--agent-portfolio)",
  interview_prep: "var(--agent-interview)",
};

// Maps a Biggest Opportunity module name to the agent whose bid it actually
// drives — Resume has no dedicated agent, its score feeds skill_agent's bid.
const OPPORTUNITY_TO_AGENT = {
  Resume: "skill_building",
  Portfolio: "portfolio",
  Networking: "networking",
  Interview: "interview_prep",
};

function AllocationCompetition({ bids, allocation, opportunity }) {
  if (!bids || !allocation) return null;

  const allocationByAgent = {};
  allocation.allocations.forEach((a) => {
    allocationByAgent[a.agent] = a.hours;
  });

  const totalHours = allocation.allocations.reduce((sum, a) => sum + a.hours, 0);

  const topAgent = allocation.allocations.reduce(
    (top, a) => (a.hours > (allocationByAgent[top] ?? -1) ? a.agent : top),
    allocation.allocations[0]?.agent
  );

  const opportunityAgent = opportunity ? OPPORTUNITY_TO_AGENT[opportunity.module] : null;
  const isAligned = Boolean(opportunityAgent) && topAgent === opportunityAgent;

  const maxValue = Math.max(
    ...bids.map((b) => Math.max(b.requested_hours, allocationByAgent[b.agent] || 0)),
    1
  );

  return (
    <div className="competition-wrap">
      <div className="competition-header">
        <span className="competition-hours">{totalHours}</span>
        <span className="competition-hours-label">HOURS AVAILABLE</span>
      </div>

      {isAligned ? (
        <p className="competition-caption">
          {AGENT_LABELS[opportunityAgent]} received the largest share this week — it's
          currently your biggest opportunity.
        </p>
      ) : (
        <p className="competition-caption">
          Here's how your available hours were divided across four competing priorities this week.
        </p>
      )}

      <div className="competition-rows">
        {bids.map((bid) => {
          const allocated = allocationByAgent[bid.agent] || 0;
          const isHighlighted = bid.agent === opportunityAgent;
          return (
            <div key={bid.agent} className={`competition-row ${isHighlighted ? "highlighted" : ""}`}>
              <span className="competition-agent-label">{AGENT_LABELS[bid.agent]}</span>
              <div className="competition-bars">
                <div className="competition-bar-track">
                  <div
                    className="competition-bar-requested"
                    style={{ width: `${(bid.requested_hours / maxValue) * 100}%` }}
                  />
                </div>
                <div className="competition-bar-track">
                  <div
                    className="competition-bar-allocated"
                    style={{ width: `${(allocated / maxValue) * 100}%`, background: AGENT_COLORS[bid.agent] }}
                  />
                </div>
              </div>
              <span className="competition-values">
                requested {bid.requested_hours}h → got {allocated}h
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default AllocationCompetition;