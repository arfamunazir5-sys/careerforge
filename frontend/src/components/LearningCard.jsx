import Card from "../ui/Card";
import Badge from "../ui/Badge";
import { agentMeta } from "../ui/agentMeta";
import "./Phase2.css";
import "./Phase6.css";

const ORDER = ["skill_building", "portfolio", "networking", "interview_prep"];

function LearningCard({ learning }) {
  if (!learning) return null;

  const hasAny = ORDER.some((a) => learning[a] && learning[a].total > 0);

  return (
    <Card
      title="What CareerForge has learned from you"
      subtitle="Agents whose tasks you keep ignoring get a smaller share, never less than 70% of their normal weight"
    >
      {!hasAny ? (
        <p className="p2-text">
          Nothing yet. Complete or ignore tasks in your weekly plan and the agents will adjust to what
          you actually do.
        </p>
      ) : (
        <div className="lr-list">
          {ORDER.map((agent) => {
            const info = learning[agent];
            if (!info) return null;
            const lowered = info.multiplier < 1;
            return (
              <div key={agent} className="lr-row">
                <div className="lr-head">
                  <Badge agent={agent} />
                  {lowered ? (
                    <Badge tone="warning">{`Weight x${info.multiplier.toFixed(2)}`}</Badge>
                  ) : (
                    <Badge>No adjustment</Badge>
                  )}
                </div>
                <div className="lr-track">
                  <div
                    className="lr-fill"
                    style={{
                      width: `${info.total ? (info.followed / info.total) * 100 : 0}%`,
                      background: agentMeta(agent).color,
                    }}
                  />
                </div>
                <div className="lr-meta" style={{ marginTop: 6 }}>
                  {info.total
                    ? `Completed ${info.followed} of your last ${info.total} ${info.total === 1 ? "task" : "tasks"}`
                    : "No tasks completed or ignored yet"}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}

export default LearningCard;