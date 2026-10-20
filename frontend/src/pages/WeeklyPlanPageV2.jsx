import { useState, useEffect } from "react";
import { Sparkles, Download } from "lucide-react";
import { api, API_BASE_URL } from "../api/client";
import TaskCardV2 from "../components/TaskCardV2";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import ProgressRing from "../ui/ProgressRing";
import { SkeletonCard } from "../ui/Skeleton";
import { agentMeta } from "../ui/agentMeta";
import "../components/VisualV2.css";
import "./PagesV2.css";
import "./DayView.css";

// Same rule the backend calendar export uses: task N goes on weekday N % 7,
// counting from this week's Monday, starting at 6 PM.
function weekStartMonday() {
  const now = new Date();
  const d = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  return d;
}

function formatDay(start, offset) {
  const d = new Date(start);
  d.setDate(start.getDate() + offset);
  return d.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" });
}

function WeeklyPlanPageV2({ onTaskUpdate }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [busyTaskId, setBusyTaskId] = useState(null);
  const [error, setError] = useState(null);
  const [view, setView] = useState("status");

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
    <button className="btn-primary with-icon" onClick={handleGeneratePlan} disabled={generating}>
      <Sparkles size={16} aria-hidden="true" />
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

  // Day view: original plan order, same rule as the calendar export.
  const byDay = Array.from({ length: 7 }, () => []);
  tasks.forEach((t, i) => byDay[i % 7].push(t));
  const weekStart = weekStartMonday();
  const dayGroups = byDay
    .map((list, offset) => ({ offset, list }))
    .filter((g) => g.list.length > 0);

  const calendarLink = (
    <a
      className="pw-link"
      href={`${API_BASE_URL}/export-calendar`}
      target="_blank"
      rel="noopener noreferrer"
    >
      <Download size={14} aria-hidden="true" />
      Calendar (.ics)
    </a>
  );

  return (
    <div className="cf-page">
      <div className="pw-header">
        <div>
          <h2 className="pw-title">This Week's Plan</h2>
          <p className="pw-subtitle">Your allocation, broken down into concrete work.</p>
        </div>
        <div className="pw-actions">{generateButton}</div>
      </div>

      <div className="pw-stack">
        {error && <div className="pw-banner">{error}</div>}

        <Card title="Week progress" action={calendarLink}>
          <div className="pw-ring-row">
            <ProgressRing
              value={pct}
              size={96}
              stroke={10}
              color="var(--cf-agent-skill)"
              label={`${pct}%`}
              sublabel="handled"
            />
            <div className="pw-ring-text">
              <div className="pw-progress-count">
                {handledCount} / {tasks.length}
              </div>
              <div className="pw-progress-label">
                tasks handled &middot; {doneHours}h of {totalHours}h completed
              </div>
            </div>
          </div>
          {tasks.length > 0 && pendingTasks.length === 0 && (
            <div className="pw-banner pw-banner-success" style={{ marginTop: "var(--cf-space-3)" }}>
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

        <div className="pw-toggle" role="group" aria-label="Task view">
          <button
            type="button"
            className={view === "status" ? "active" : ""}
            onClick={() => setView("status")}
          >
            By status
          </button>
          <button
            type="button"
            className={view === "day" ? "active" : ""}
            onClick={() => setView("day")}
          >
            By day
          </button>
        </div>

        {view === "status" ? (
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
        ) : (
          <div className="pw-day-list">
            <p className="pw-note">
              Suggested schedule: tasks are placed Monday first, one per day, at 6:00 PM. This is the
              same schedule the calendar export uses. Marking a task done does not move it.
            </p>
            {dayGroups.map((g) => {
              const dayHours = g.list.reduce((sum, t) => sum + t.hours, 0);
              const dayDone = g.list.filter((t) => t.status === "done").length;
              return (
                <section key={g.offset}>
                  <header className="pw-day-head">
                    <span className="pw-day-name">{formatDay(weekStart, g.offset)}</span>
                    <span className="pw-day-meta">
                      from 6:00 PM &middot; {dayHours}h &middot; {dayDone}/{g.list.length} done
                    </span>
                  </header>
                  <div className="pw-task-list">
                    {g.list.map((task) => (
                      <TaskCardV2
                        key={task.id}
                        task={task}
                        onAction={handleTaskAction}
                        disabled={busyTaskId !== null}
                      />
                    ))}
                  </div>
                </section>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default WeeklyPlanPageV2;