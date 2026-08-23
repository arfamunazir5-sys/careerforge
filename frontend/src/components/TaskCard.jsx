const AGENT_COLORS = {
  skill_building: "var(--agent-skill)",
  networking: "var(--agent-networking)",
  portfolio: "var(--agent-portfolio)",
  interview_prep: "var(--agent-interview)",
};

const AGENT_LABELS = {
  skill_building: "Skill Building",
  networking: "Networking",
  portfolio: "Portfolio",
  interview_prep: "Interview Prep",
};

function TaskCard({ task, onAction }) {
  const color = AGENT_COLORS[task.agent] || "var(--color-ink)";

  return (
    <div className={`task-card ${task.status}`} style={{ "--task-color": color }}>
      <div className="task-info">
        <h4>{task.title}</h4>
        <span className="task-meta">
          {AGENT_LABELS[task.agent] || task.agent} &middot; {task.hours}h
        </span>
      </div>

      {task.status === "pending" ? (
        <div className="task-actions">
          <button className="btn-done" onClick={() => onAction(task.id, "done")}>Done</button>
          <button className="btn-ignore" onClick={() => onAction(task.id, "ignored")}>Ignore</button>
        </div>
      ) : (
        <span className="task-meta">{task.status}</span>
      )}
    </div>
  );
}

export default TaskCard;