import { useState, useEffect } from "react";
import { api } from "../api/client";
import AllocationCompetitionV2 from "../components/AllocationCompetitionV2";
import SkillPathV2 from "../components/SkillPathV2";
import AdaptationPanelV2 from "../components/AdaptationPanelV2";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import SectionHeader from "../ui/SectionHeader";
import ProgressRing from "../ui/ProgressRing";
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

function ringColor(score) {
  if (score >= 70) return "var(--cf-success)";
  if (score >= 50) return "var(--cf-primary)";
  return "var(--cf-warning)";
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
          <SkeletonCard lines={3} />
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
        <Card>
          <div className="cc-hero">
            <ProgressRing
              value={health.overall_score}
              size={140}
              stroke={13}
              color={ringColor(health.overall_score)}
              label={health.overall_score}
              sublabel="/ 100"
            />
            <div className="cc-hero-body">
              <Badge tone="primary">Career Health Score</Badge>
              <h2 className="cc-hero-title">{health.label || "Your overall readiness"}</h2>
              <p className="cc-subtitle">
                Combined from your resume, portfolio, networking and interview scores.
              </p>
              <div className="cc-hero-chips">
                {strongest && (
                  <Badge tone="success">{`Strongest: ${strongest.name} ${strongest.score}`}</Badge>
                )}
                {weakest && (
                  <Badge tone="warning">{`Needs work: ${weakest.name} ${weakest.score}`}</Badge>
                )}
              </div>
            </div>
          </div>
        </Card>

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