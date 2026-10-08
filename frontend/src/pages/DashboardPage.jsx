import { useState, useEffect } from "react";
import { api } from "../api/client";
import AllocationCompetition from "../components/AllocationCompetition";
import SkillPath from "../components/SkillPath";

function DashboardPage({ refreshKey }) {
  const [health, setHealth] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [opportunity, setOpportunity] = useState(null);
  const [bids, setBids] = useState(null);
  const [allocation, setAllocation] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getDashboard()
      .then((data) => {
        setHealth(data.career_health);
        setExplanation(data.explanations);
        setOpportunity(data.biggest_opportunity);
        setBids(data.bids);
        setAllocation(data.allocation);
      })
      .catch((err) => setError(err.message));
  }, [refreshKey]);

  if (error) return <p className="error-text">{error}</p>;
  if (!health || !explanation) return <p className="status-text">Loading dashboard...</p>;

  return (
    <section className="dashboard-page">
      <h2>Career Health Score</h2>
      <div className="health-score-wrap">
        <div className="overall-score">
          <span className="overall-score-value">{health.overall_score}</span>
          <span className="overall-score-label">/ 100 overall</span>
        </div>
        <div className="module-scores">
          {health.modules.map((m) => (
            <div key={m.name} className="module-score-row">
              <span className="module-score-name">{m.name}</span>
              <div className="module-score-bar-track">
                <div className="module-score-bar-fill" style={{ width: `${m.score}%` }} />
              </div>
              <span className="module-score-value">{m.score}</span>
            </div>
          ))}
        </div>
      </div>

      {opportunity && (
        <div className="opportunity-card">
          <span className="opportunity-label">Biggest Opportunity</span>
          <h3>{opportunity.module}</h3>
          <p>{opportunity.note}</p>
        </div>
      )}

      <AllocationCompetition bids={bids} allocation={allocation} opportunity={opportunity} />

      <h2>Why This Week's Allocation</h2>
      <div className="explanation-list">
        {explanation.items.map((item) => (
          <p key={item.agent} className="explanation-item">{item.explanation}</p>
        ))}
      </div>
      <SkillPath refreshKey={refreshKey} />
    </section>
    
  );
}

export default DashboardPage;