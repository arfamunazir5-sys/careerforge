import Card from "../ui/Card";
import Badge from "../ui/Badge";
import "./VisualV2.css";

function fmt(n) {
  return n > 0 ? `+${n}` : `${n}`;
}

function progressTone(n) {
  if (n > 0) return "success";
  if (n < 0) return "danger";
  return "neutral";
}

function hoursTone(n) {
  return n === 0 ? "neutral" : "info";
}

function AdaptationPanelV2({ adaptation }) {
  if (!adaptation) return null;
  const { progress = [], reallocation = [] } = adaptation;

  if (progress.length === 0 && reallocation.length === 0) {
    return (
      <Card title="Adaptation" subtitle="Shown only when something has really changed">
        <div className="v2-empty">
          Complete tasks from this week's plan and your progress will show up here. When you
          regenerate your plan, you will see how your hours shifted in response.
        </div>
      </Card>
    );
  }

  return (
    <Card title="Adaptation" subtitle="Real changes only, nothing is shown unless a score or allocation moved">
      {progress.length > 0 && (
        <>
          <span className="v2-section-label">Progress since this plan was generated</span>
          {progress.map((p) => (
            <div key={p.module} className="v2-adapt-row">
              <span className="v2-adapt-name">{p.module}</span>
              <span className="v2-adapt-values">
                {p.before} &rarr; {p.after}
                <Badge tone={progressTone(p.change)}>{fmt(p.change)}</Badge>
              </span>
            </div>
          ))}
        </>
      )}

      {reallocation.length > 0 && (
        <>
          <span className="v2-section-label">How your hours shifted from the previous plan</span>
          {reallocation.map((r) => {
            const diff = r.after - r.before;
            return (
              <div key={r.agent}>
                <div className="v2-adapt-row">
                  <Badge agent={r.agent} />
                  <span className="v2-adapt-values">
                    {r.before}h &rarr; {r.after}h
                    <Badge tone={hoursTone(diff)}>{`${fmt(diff)}h`}</Badge>
                  </span>
                </div>
                {r.note && <p className="v2-adapt-note">{r.note}</p>}
              </div>
            );
          })}
        </>
      )}
    </Card>
  );
}

export default AdaptationPanelV2;