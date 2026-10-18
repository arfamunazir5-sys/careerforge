import Badge from "../ui/Badge";
import { agentMeta } from "../ui/agentMeta";
import "../pages/PagesV2.css";

function TaskCardV2({ task, onAction, disabled = false }) {
  const meta = agentMeta(task.agent);
  const isPending = task.status === "pending";

  return (
    <div className={`tc2-card tc2-${task.status}`} style={{ "--task-color": meta.color }}>
      <div className="tc2-info">
        <h4 className="tc2-title">{task.title}</h4>
        <div className="tc2-meta">
          <Badge agent={task.agent} />
          <span className="tc2-hours">{task.hours}h</span>
        </div>
      </div>

      {isPending ? (
        <div className="tc2-actions">
          <button
            className="btn-done"
            disabled={disabled}
            onClick={() => onAction(task.id, "done")}
          >
            Done
          </button>
          <button
            className="btn-ignore"
            disabled={disabled}
            onClick={() => onAction(task.id, "ignored")}
          >
            Ignore
          </button>
        </div>
      ) : (
        <Badge tone={task.status === "done" ? "success" : "neutral"}>
          {task.status === "done" ? "Done" : "Ignored"}
        </Badge>
      )}
    </div>
  );
}

export default TaskCardV2;