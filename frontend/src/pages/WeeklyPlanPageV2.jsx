import { useState, useEffect } from "react";
import { api, API_BASE_URL } from "../api/client";
import TaskCardV2 from "../components/TaskCardV2";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { SkeletonCard } from "../ui/Skeleton";
import { agentMeta } from "../ui/agentMeta";
import "../components/VisualV2.css";
import "./PagesV2.css";

function WeeklyPlanPageV2({ onTaskUpdate }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [busyTaskId, setBusyTaskId] = useState(null);
  const [error, setError] = useState(null);

  const loadPlan = async (showSpinner = true) => {
    if (showSpinner) setLoading(true);
    setError(null);
    try {
      const data = await api.getPlan();
      setPlan(data);
    } catch (err) {
      setPlan(null);
      setError(err.message);
    } finally {
      if (showSpinner) setLoading(false);
    }
  };

  useEffect(() => {
    loadPlan();
  }, []);

  const handleGeneratePlan = async () => {
    setGenerating(true);
    setError(null);
    try {
      const data = await api.generatePlan();
      setPlan(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleTaskAction = async (taskId, action) => {
    if (busyTaskId) return;
    setBusyTaskId(taskId);
    setError(null);
    try {
      if (action === "done") {
        await api.completeTask(taskId);
      } else {
        await api.ignoreTask(taskId);
      }
      await loadPlan(false);
      if (onTaskUpdate) onTaskUpdate();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyTaskId(null);
    }
  };

  const generateButton = (
    <button className="btn-primary" onClick={handleGeneratePlan} disabled={generating}>
      {generating ? "Generating..." : plan ? "Generate New Plan" : "Generate My Plan"}
    </button>
  );

  if (loading) {
    return (
      <div className="cf-page pw-stack">
        <SkeletonCard lines={2} />
        <SkeletonCard lines={1} />
        <SkeletonCard lines={2} title={false} />
        <SkeletonCard lines={2} title={false} />
      </div>
    );
  }

  if (!plan && error) {
    return (
      <div className="cf-page">
        <ErrorState message={error} onRetry={() => loadPlan()} />
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="cf-page">
        <EmptyState
          title="No plan yet"
          message="Generate this week's plan and CareerForge will turn your allocation into concrete tasks."
          action={generateButton}
        />
      </div>
    );
  }

  const tasks = plan.tasks || [];
  const totalHours = tasks.reduce((sum, t) => sum + t.hours, 0);
  const doneTasks = tasks.filter((t) => t.status === "done");
  const ignoredTasks = tasks.filter((t) => t.status === "ignored");
  const pendingTasks = tasks.filter((t) => t.status === "pending");
  const handledCount = doneTasks.length + ignoredTasks.length;
  const doneHours = doneTasks.reduce((sum, t) => sum + t.hours, 0);
  const pct = tasks.length ? Math.round((handledCount / tasks.length) * 100) : 0;

  const hoursByAgent = {};
  tasks.forEach((t) => {
    hoursByAgent[t.agent] = (hoursByAgent[t.agent] || 0) + t.hours;
  });
  const segments = Object.entries(hoursByAgent)
    .filter(([, h]) => h > 0)
    .sort((a, b) => b[1] - a[1]);

  const ordered = [...pendingTasks, ...doneTasks, ...ignoredTasks];

  return (
    <div className="cf-page">
      <div className="pw-header">
        <div>
          <h2 className="pw-title">This Week's Plan</h2>
          <p className="pw-subtitle">Your allocation, broken down into concrete work.</p>
        </div>
        <div className="pw-actions">
          {generateButton}
          <a
            className="btn-secondary"
            href={`${API_BASE_URL}/export-calendar`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Export to Calendar
          </a>
        </div>
      </div>

      <div className="pw-stack">
        {error && <div className="pw-banner">{error}</div>}

        <Card title="Week progress">
          <div className="pw-progress-line">
            <span className="pw-progress-count">
              {handledCount} / {tasks.length}
            </span>
            <span className="pw-progress-label">
              tasks handled &middot; {doneHours}h of {totalHours}h completed
            </span>
          </div>
          <div className="v2-meter">
            <div className="v2-meter-fill" style={{ width: `${pct}%` }} />
          </div>
          {tasks.length > 0 && pendingTasks.length === 0 && (
            <div className="pw-banner pw-banner-success">
              Every task is handled. Generate a new plan to see how your hours adapt.
            </div>
          )}
          <p className="pw-note">
            These {totalHours}h of tasks are this week's allocation, broken down into concrete work.
          </p>
        </Card>

        {segments.length > 0 && totalHours > 0 && (
          <Card title="Hours by agent" subtitle="How this week's allocation was split">
            <div className="v2-stack">
              {segments.map(([agent, hours]) => {
                const w = (hours / totalHours) * 100;
                return (
                  <div
                    key={agent}
                    className="v2-stack-seg"
                    style={{ width: `${w}%`, background: agentMeta(agent).color }}
                    title={`${agentMeta(agent).label}: ${hours}h`}
                  >
                    {w >= 12 ? `${hours}h` : ""}
                  </div>
                );
              })}
            </div>
            <div className="v2-legend">
              {segments.map(([agent, hours]) => (
                <Badge key={agent} agent={agent}>
                  {`${agentMeta(agent).label} ${hours}h`}
                </Badge>
              ))}
            </div>
          </Card>
        )}

        <div className="pw-task-list">
          {ordered.map((task) => (
            <TaskCardV2
              key={task.id}
              task={task}
              onAction={handleTaskAction}
              disabled={busyTaskId !== null}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default WeeklyPlanPageV2;