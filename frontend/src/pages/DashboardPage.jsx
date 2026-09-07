import { useState, useEffect } from "react";
import { api } from "../api/client";

function DashboardPage() {
  const [health, setHealth] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
  api.getDashboard()
    .then((data) => {
      setHealth(data.career_health);
      setExplanation(data.explanations);
    })
    .catch((err) => setError(err.message));
}, []);

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

      <h2>Why This Week's Allocation</h2>
      <div className="explanation-list">
        {explanation.items.map((item) => (
          <p key={item.agent} className="explanation-item">{item.explanation}</p>
        ))}
      </div>
    </section>
  );
}

export default DashboardPage;