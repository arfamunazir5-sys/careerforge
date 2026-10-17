import { useState, useEffect } from "react";
import { api } from "../api/client";
import Card from "../ui/Card";
import "./VisualV2.css";

function SkillPathV2({ refreshKey }) {
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    api.getSkillProgress().then(setProgress).catch(() => setProgress(null));
  }, [refreshKey]);

  if (!progress) return null;

  const chain = progress.full_chain || [];
  const doneCount = chain.filter((s) => progress.completed_skills.includes(s)).length;
  const pct = chain.length ? Math.round((doneCount / chain.length) * 100) : 0;
  const role = String(progress.target_role || "").replace(/_/g, " ");

  return (
    <Card
      title="Skill path"
      subtitle={`${role}: ${doneCount} of ${chain.length} skills complete`}
    >
      <div className="v2-meter">
        <div className="v2-meter-fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="v2-chips">
        {chain.map((skill) => {
          const isDone = progress.completed_skills.includes(skill);
          const isNext = skill === progress.next_skill;
          const cls = isDone ? "v2-chip done" : isNext ? "v2-chip next" : "v2-chip";
          return (
            <span key={skill} className={cls}>
              {isDone ? "\u2713 " : ""}
              {skill.replace(/_/g, " ")}
            </span>
          );
        })}
      </div>
    </Card>
  );
}

export default SkillPathV2;