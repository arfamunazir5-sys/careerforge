import { useState, useEffect } from "react";
import { api } from "../api/client";
import AllocationCompetitionV2 from "../components/AllocationCompetitionV2";
import SkillPathV2 from "../components/SkillPathV2";
import AdaptationPanelV2 from "../components/AdaptationPanelV2";
import Card from "../ui/Card";
import StatCard from "../ui/StatCard";
import Badge from "../ui/Badge";
import SectionHeader from "../ui/SectionHeader";
import { SkeletonCard } from "../ui/Skeleton";
import ErrorState from "../ui/ErrorState";
import { agentMeta } from "../ui/agentMeta";
import "./CommandCenter.css";

function moduleColor(name) {
  const n = String(name || "").toLowerCase();
  if (n.includes("portfolio")) return agentMeta("portfolio").color;
  if (n.includes("network")) return agentMeta("networking").color;
  if (n.includes("interview")) return agentMeta("interview_prep").color;
  if (n.includes("skill") || n.includes("resume")) return agentMeta("skill_building").color;
  return "var(--cf-primary)";
}

function scoreTone(score) {
  if (score >= 70) return "success";
  if (score >= 50) return "primary";
  return "warning";
}

function CommandCenterPage({ refreshKey }) {
  const [health, setHealth] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [opportunity, setOpportunity] = useState(null);
  const [bids, setBids] = useState(null);
  const [allocation, setAllocation] = useState(null);
  const [adaptation, setAdaptation] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getDashboard()
      .then((data) => {
        setHealth(data.career_health);
        setExplanation(data.explanations);
        setOpportunity(data.biggest_opportunity);
        setBids(data.bids);
        setAllocation(data.allocation);
        setAdaptation(data.adaptation);
      })
      .catch((err) => setError(err.message));
  }, [refreshKey]);

  if (error) {
    return (
      <div className="cf-page">
        <ErrorState message={error} onRetry={() => window.location.reload()} />
      </div>
    );
  }

  if (!health || !explanation) {
    return (
      <div className="cf-page">
        <header className="cc-header">
          <h1 className="cc-title">Command Center</h1>
          <p className="cc-subtitle">Loading your dashboard...</p>
        </header>
        <div className="cc-stack">
          <div className="cf-grid cf-grid-3">
            <SkeletonCard lines={2} />
            <SkeletonCard lines={2} />
            <SkeletonCard lines={2} />
          </div>
          <SkeletonCard lines={5} />
          <SkeletonCard lines={4} />
        </div>
      </div>
    );
  }

  const modules = health.modules || [];
  const strongest = modules.length
    ? modules.reduce((a, b) => (b.score > a.score ? b : a))
    : null;
  const weakest = modules.length
    ? modules.reduce((a, b) => (b.score < a.score ? b : a))
    : null;

  return (
    <div className="cf-page">
      <header className="cc-header">
        <h1 className="cc-title">Command Center</h1>
        <p className="cc-subtitle">
          Your career health, this week's decisions, and how the plan is adapting.
        </p>
      </header>

      <div className="cc-stack">
        <div className="cf-grid cf-grid-3">
          <StatCard
            label="Career health"
            value={`${health.overall_score} / 100`}
            hint={health.label || "Overall score"}
            tone={scoreTone(health.overall_score)}
          />
          {strongest && (
            <StatCard
              label="Strongest area"
              value={strongest.name}
              hint={`Score ${strongest.score}`}
              tone="success"
            />
          )}
          {weakest && (
            <StatCard
              label="Needs most work"
              value={weakest.name}
              hint={`Score ${weakest.score}`}
              tone="warning"
            />
          )}
        </div>

        <Card title="Module scores" subtitle="Where you stand in each area">
          <div className="cc-modules">
            {modules.map((m) => (
              <div key={m.name} className="cc-module-row">
                <span className="cc-module-name">{m.name}</span>
                <div className="cc-track">
                  <div
                    className="cc-fill"
                    style={{ width: `${m.score}%`, background: moduleColor(m.name) }}
                  />
                </div>
                <span className="cc-module-value">{m.score}</span>
              </div>
            ))}
          </div>
        </Card>

        {opportunity && (
          <Card accent="var(--cf-agent-portfolio)">
            <Badge tone="warning">Biggest Opportunity</Badge>
            <h3 className="cc-opportunity-title">{opportunity.module}</h3>
            <p className="cc-opportunity-note">{opportunity.note}</p>
          </Card>
        )}

        <AllocationCompetitionV2 bids={bids} allocation={allocation} opportunity={opportunity} />

        <SectionHeader
          title="Why this week's allocation"
          subtitle="What each agent argued for, in plain language"
        />
        <Card>
          {explanation.items.map((item) => (
            <div key={item.agent} className="cc-explain-item">
              <Badge agent={item.agent} />
              <p className="cc-explain-text">{item.explanation}</p>
            </div>
          ))}
        </Card>

        <AdaptationPanelV2 adaptation={adaptation} />

        <SkillPathV2 refreshKey={refreshKey} />
      </div>
    </div>
  );
}

export default CommandCenterPage;