import { useState, useEffect } from "react";
import { rolesApi } from "../api/roles";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import { agentMeta } from "../ui/agentMeta";
import "./Phase2.css";
import "./Phase4.css";

const ORDER = ["skill_building", "portfolio", "networking", "interview_prep"];

function RoleSimulator({ refreshKey }) {
  const [sims, setSims] = useState(null);

  useEffect(() => {
    rolesApi.simulate().then(setSims).catch(() => setSims(null));
  }, [refreshKey]);

  if (!sims) return null;

  return (
    <Card
      title="What if you chose a different role?"
      subtitle="Your current scores and hours, weighted for each role. Nothing is saved."
    >
      <div className="rs-list">
        {sims.map((s) => {
          const total = ORDER.reduce((sum, a) => sum + (s.hours[a] || 0), 0);
          return (
            <div key={s.role} className={`rs-row ${s.is_current ? "current" : ""}`}>
              <div className="rs-head">
                <strong>{s.label}</strong>
                {s.is_current && <Badge tone="primary">Your role</Badge>}
                <span className="rs-health">Health {s.health}</span>
              </div>
              <div className="rs-bar">
                {ORDER.filter((a) => (s.hours[a] || 0) > 0).map((a) => (
                  <div
                    key={a}
                    className="rs-seg"
                    style={{ width: `${(s.hours[a] / total) * 100}%`, background: agentMeta(a).color }}
                    title={`${agentMeta(a).label}: ${s.hours[a]}h`}
                  />
                ))}
              </div>
              <div className="rs-hours">
                {ORDER.map((a) => (
                  <span key={a}>{`${agentMeta(a).short} ${s.hours[a] || 0}h`}</span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
      <p className="p2-text" style={{ marginTop: "var(--cf-space-3)" }}>
        Resume and quiz results were measured for your current role, so the other roles are estimates.
      </p>
    </Card>
  );
}

export default RoleSimulator;