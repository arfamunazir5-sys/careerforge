import { useState, useEffect } from "react";
import { api } from "../api/client";

function StateHeader({ refreshKey }) {
  const [state, setState] = useState(null);

  useEffect(() => {
    api.getState().then(setState).catch(() => setState(null));
  }, [refreshKey]);

  if (!state) return null;

  return (
    <header className="state-header">
      <div className="brand">
        <h1>CareerForge</h1>
        <span className="role-tag">{state.target_role.replace("_", " ")}</span>
      </div>
      <div className="score-strip">
        <ScoreItem label="Resume" value={state.resume_score} />
        <ScoreItem label="Portfolio" value={state.portfolio_score} />
        <ScoreItem label="Networking" value={state.networking_score} />
        <ScoreItem label="Interview" value={state.interview_score} />
        <ScoreItem label="Task streak" value={state.streak_count} />
        <ScoreItem label="Week" value={state.week_number} />
      </div>
    </header>
  );
}

function ScoreItem({ label, value }) {
  return (
    <div className="score-item">
      <span className="score-value">{value}</span>
      <span className="score-label">{label}</span>
    </div>
  );
}

export default StateHeader;