import Card from "../ui/Card";
import Badge from "../ui/Badge";
import { agentMeta } from "../ui/agentMeta";
import "./VisualV2.css";
import "./Phase2.css";

// Resume has no dedicated agent; its score feeds the skill agent's bid.
const OPPORTUNITY_TO_AGENT = {
  Resume: "skill_building",
  Portfolio: "portfolio",
  Networking: "networking",
  Interview: "interview_prep",
};

function AllocationCompetitionV2({ bids, allocation, opportunity, shares }) {
  if (!bids || !allocation) return null;

  const hoursByAgent = {};
  allocation.allocations.forEach((a) => {
    hoursByAgent[a.agent] = a.hours;
  });

  const totalHours = allocation.allocations.reduce((sum, a) => sum + a.hours, 0);

  const topAgent = allocation.allocations.reduce(
    (top, a) => (a.hours > (hoursByAgent[top] ?? -1) ? a.agent : top),
    allocation.allocations[0]?.agent
  );

  const opportunityAgent = opportunity ? OPPORTUNITY_TO_AGENT[opportunity.module] : null;
  const isAligned = Boolean(opportunityAgent) && topAgent === opportunityAgent;

  const shareOf = (agent) => {
    if (shares && shares[agent] !== undefined) return shares[agent];
    return totalHours ? Math.round(((hoursByAgent[agent] || 0) / totalHours) * 1000) / 10 : 0;
  };

  const segments = [...allocation.allocations]
    .filter((a) => a.hours > 0)
    .sort((a, b) => b.hours - a.hours);

  const rows = [...bids].sort((a, b) => (hoursByAgent[b.agent] || 0) - (hoursByAgent[a.agent] || 0));

  return (
    <Card title="This week's allocation" subtitle="Four agents competed for your hours">
      <div className="v2-alloc-top">
        <span className="v2-alloc-hours">{totalHours}</span>
        <span className="v2-alloc-hours-label">hours available</span>
      </div>

      <p className="v2-caption">
        {isAligned
          ? `${agentMeta(opportunityAgent).label} received the largest share this week, and it is currently your biggest opportunity.`
          : "Here is how your available hours were divided across four competing priorities this week."}
      </p>

      {totalHours > 0 && (
        <>
          <div className="v2-stack">
            {segments.map((a) => {
              const pct = (a.hours / totalHours) * 100;
              return (
                <div
                  key={a.agent}
                  className="v2-stack-seg"
                  style={{ width: `${pct}%`, background: agentMeta(a.agent).color }}
                  title={`${agentMeta(a.agent).label}: ${a.hours}h`}
                >
                  {pct >= 12 ? `${a.hours}h` : ""}
                </div>
              );
            })}
          </div>
          <div className="v2-legend">
            {segments.map((a) => (
              <Badge key={a.agent} agent={a.agent}>
                {`${agentMeta(a.agent).label} ${a.hours}h`}
              </Badge>
            ))}
          </div>
        </>
      )}

      <p className="v2-legend-key">
        Bid strength (0 to 1) is how strongly an agent argued for time. Share of week is its bid
        multiplied by your role's weight and your follow-through weight, divided across all four agents.
      </p>

      <div className="v2-rows">
        {rows.map((bid) => {
          const hours = hoursByAgent[bid.agent] || 0;
          const share = shareOf(bid.agent);
          const isHighlighted = bid.agent === opportunityAgent;
          return (
            <div key={bid.agent} className={`v2-row ${isHighlighted ? "highlighted" : ""}`}>
              <div className="v2-row-top">
                <div className="v2-row-tags">
                  <Badge agent={bid.agent} />
                  {isHighlighted && <Badge tone="primary">Biggest opportunity</Badge>}
                </div>
                <span className="v2-values">
                  {hours}h &middot; {share}% of your week
                </span>
              </div>
              <div className="p2-bar-label">
                <span>Bid strength</span>
                <span>{Number(bid.bid_score).toFixed(2)}</span>
              </div>
              <div className="v2-track">
                <div
                  className="v2-bar-requested"
                  style={{ width: `${Math.min(100, bid.bid_score * 100)}%` }}
                />
              </div>
              <div className="p2-bar-label">
                <span>Share of week</span>
                <span>{share}%</span>
              </div>
              <div className="v2-track">
                <div
                  className="v2-bar-allocated"
                  style={{ width: `${Math.min(100, share)}%`, background: agentMeta(bid.agent).color }}
                />
              </div>
              {bid.reason && <p className="v2-reason">{bid.reason}</p>}
            </div>
          );
        })}
      </div>
    </Card>
  );
}

export default AllocationCompetitionV2;