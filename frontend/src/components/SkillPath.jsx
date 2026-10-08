import { useState, useEffect } from "react";
import { api } from "../api/client";

function SkillPath({ refreshKey }) {
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    api.getSkillProgress().then(setProgress).catch(() => setProgress(null));
  }, [refreshKey]);

  if (!progress) return null;

  return (
    <div className="skill-path-wrap">
      <span className="skill-path-label">Skill Path — {progress.target_role.replace("_", " ")}</span>
      <div className="skill-path-chips">
        {progress.full_chain.map((skill) => {
          const isDone = progress.completed_skills.includes(skill);
          const isNext = skill === progress.next_skill;
          const className = isDone ? "skill-chip done" : isNext ? "skill-chip next" : "skill-chip";
          return (
            <span key={skill} className={className}>
              {skill.replace("_", " ")}
            </span>
          );
        })}
      </div>
    </div>
  );
}

export default SkillPath;