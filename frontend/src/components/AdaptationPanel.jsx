const AGENT_LABELS = {
  skill_building: "Skill Building",
  networking: "Networking",
  portfolio: "Portfolio",
  interview_prep: "Interview Prep",
};

function AdaptationPanel({ adaptation }) {
  if (!adaptation) return null;
  const { progress = [], reallocation = [] } = adaptation;

  if (progress.length === 0 && reallocation.length === 0) {
    return (
      <div className="adaptation-wrap">
        <span className="adaptation-label">Adaptation</span>
        <p className="adaptation-empty">
          Complete tasks from this week's plan and your progress will show up here.
          When you regenerate your plan, you'll see how your hours shifted in response.
        </p>
      </div>
    );
  }

  return (
    <div className="adaptation-wrap">
      {progress.length > 0 && (
        <>
          <span className="adaptation-label">Progress since this plan was generated</span>
          <div className="adaptation-rows">
            {progress.map((p) => (
              <div key={p.module} className="adaptation-row">
                <span className="adaptation-name">{p.module}</span>
                <span className="adaptation-values">
                  {p.before} → {p.after}
                  <span className={p.change > 0 ? "delta-up" : "delta-down"}>
                    {p.change > 0 ? `+${p.change}` : p.change}
                  </span>
                </span>
              </div>
            ))}
          </div>
        </>
      )}

      {reallocation.length > 0 && (
        <>
          <span className="adaptation-label">How your hours shifted from the previous plan</span>
          <div className="adaptation-rows">
            {reallocation.map((r) => (
              <div key={r.agent} className="adaptation-row stacked">
                <div className="adaptation-row-top">
                  <span className="adaptation-name">{AGENT_LABELS[r.agent] || r.agent}</span>
                  <span className="adaptation-values">{r.before}h → {r.after}h</span>
                </div>
                {r.note && <p className="adaptation-note">{r.note}</p>}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default AdaptationPanel;