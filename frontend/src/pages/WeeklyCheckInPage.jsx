import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { weeklyApi } from "../api/weekly";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import { SkeletonCard } from "../ui/Skeleton";
import "../components/VisualV2.css";
import "../components/Phase5.css";
import "./PagesV2.css";

function fmt(n) {
  return n > 0 ? `+${n}` : `${n}`;
}

function ScoreChanges({ changes }) {
  const entries = Object.entries(changes || {});
  if (entries.length === 0) return null;
  return (
    <div className="wk-chips">
      {entries.map(([module, change]) => (
        <Badge key={module} tone={change > 0 ? "success" : "danger"}>{`${module} ${fmt(change)}`}</Badge>
      ))}
    </div>
  );
}

function WeeklyCheckInPage({ onWeekClosed }) {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [noPlan, setNoPlan] = useState(false);
  const [history, setHistory] = useState([]);
  const [hours, setHours] = useState("");
  const [confidence, setConfidence] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [closed, setClosed] = useState(null);

  useEffect(() => {
    Promise.all([
      api.getState(),
      weeklyApi.getSummary().catch((err) => (err.status === 404 ? null : Promise.reject(err))),
    ])
      .then(([state, sum]) => {
        setHours(String(state.available_hours));
        setHistory(state.week_history || []);
        setSummary(sum);
        setNoPlan(sum === null);
      })
      .catch((err) => setLoadError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loadError) {
    return (
      <div className="cf-page">
        <ErrorState message={loadError} onRetry={() => window.location.reload()} />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="cf-page pw-stack">
        <SkeletonCard lines={3} />
        <SkeletonCard lines={3} />
      </div>
    );
  }

  if (closed) {
    return (
      <div className="cf-page">
        <div className="pw-header">
          <div>
            <h2 className="pw-title">{`Week ${closed.closed.week_number} closed`}</h2>
            <p className="pw-subtitle">{`Week ${closed.week_number} is ready with a fresh plan.`}</p>
          </div>
        </div>
        <Card>
          <div className="wk-stats">
            <div>
              <div className="wk-stat-value">{`${closed.closed.done}/${closed.closed.tasks_total}`}</div>
              <div className="wk-stat-label">tasks done</div>
            </div>
            <div>
              <div className="wk-stat-value">{`${closed.closed.hours_done}h`}</div>
              <div className="wk-stat-label">{`of ${closed.closed.hours_total}h completed`}</div>
            </div>
          </div>
          <ScoreChanges changes={closed.closed.score_changes} />
          <div className="wk-actions">
            <button type="button" className="btn-primary" onClick={() => navigate("/")}>
              Open this week's plan
            </button>
            <button type="button" className="btn-secondary" onClick={() => navigate("/dashboard")}>
              See the Command Center
            </button>
          </div>
        </Card>
      </div>
    );
  }

  if (noPlan) {
    return (
      <div className="cf-page">
        <EmptyState
          title="No plan to close yet"
          message="Generate this week's plan first. The check-in summarises it and builds the next one."
          action={<Link className="btn-primary" to="/">Go to Weekly Plan</Link>}
        />
      </div>
    );
  }

  const hoursNum = Number(hours);
  const hoursInvalid = hours === "" || !Number.isInteger(hoursNum) || hoursNum < 1 || hoursNum > 80;

  const handleClose = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const result = await weeklyApi.nextWeek({
        available_hours: hoursNum,
        confidence: confidence === "" ? undefined : Number(confidence),
      });
      setClosed(result);
      if (onWeekClosed) onWeekClosed();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const pct = summary.tasks_total ? Math.round(((summary.done + summary.ignored) / summary.tasks_total) * 100) : 0;
  const pastWeeks = [...history].reverse();

  return (
    <div className="cf-page">
      <div className="pw-header">
        <div>
          <h2 className="pw-title">Weekly check-in</h2>
          <p className="pw-subtitle">Review this week, then start the next one.</p>
        </div>
      </div>

      <div className="pw-stack">
        <Card title={`Week ${summary.week_number} so far`}>
          <div className="wk-stats">
            <div>
              <div className="wk-stat-value">{`${summary.done}/${summary.tasks_total}`}</div>
              <div className="wk-stat-label">tasks done</div>
            </div>
            <div>
              <div className="wk-stat-value">{`${summary.hours_done}h`}</div>
              <div className="wk-stat-label">{`of ${summary.hours_total}h completed`}</div>
            </div>
            <div>
              <div className="wk-stat-value">{summary.ignored}</div>
              <div className="wk-stat-label">ignored</div>
            </div>
          </div>
          <div className="v2-meter">
            <div className="v2-meter-fill" style={{ width: `${pct}%` }} />
          </div>
          <ScoreChanges changes={summary.score_changes} />
          {summary.pending > 0 && (
            <p className="pw-note">
              {`${summary.pending} task${summary.pending === 1 ? " is" : "s are"} still pending. Pending tasks are not carried over.`}
            </p>
          )}
        </Card>

        <Card title="Start next week" subtitle="Closing builds a fresh plan from your current scores">
          <div className="wk-form-row">
            <div className="pf-field">
              <label className="pf-label" htmlFor="wk-hours">Hours available next week</label>
              <input
                id="wk-hours"
                type="number"
                min="1"
                max="80"
                className={`pf-input ${hoursInvalid ? "invalid" : ""}`}
                value={hours}
                onChange={(e) => setHours(e.target.value)}
              />
              {hoursInvalid && <span className="pf-error">Enter a whole number between 1 and 80.</span>}
            </div>
            <div className="pf-field">
              <label className="pf-label" htmlFor="wk-confidence">Interview confidence (optional)</label>
              <select
                id="wk-confidence"
                className="pf-input"
                value={confidence}
                onChange={(e) => setConfidence(e.target.value)}
              >
                <option value="">Keep current</option>
                {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
                  <option key={n} value={n}>{`${n} / 10`}</option>
                ))}
              </select>
            </div>
          </div>
          {error && <div className="pw-banner">{error}</div>}
          <button
            type="button"
            className="btn-primary pf-submit"
            onClick={handleClose}
            disabled={submitting || hoursInvalid}
          >
            {submitting ? "Closing..." : `Close week ${summary.week_number} and start week ${summary.week_number + 1}`}
          </button>
        </Card>

        <Card title="Past weeks" subtitle={pastWeeks.length ? "Your last closed weeks" : "Closed weeks appear here"}>
          {pastWeeks.length === 0 ? (
            <p className="pw-note" style={{ margin: 0 }}>Nothing yet. Close your first week to start the log.</p>
          ) : (
            pastWeeks.map((w) => (
              <div key={`${w.week_number}-${w.role}`} className="wk-row">
                <span>{`Week ${w.week_number}`}</span>
                <span className="wk-row-meta">
                  {`${w.done}/${w.tasks_total} tasks · ${w.hours_done}h of ${w.hours_total}h`}
                </span>
                <ScoreChanges changes={w.score_changes} />
              </div>
            ))
          )}
        </Card>
      </div>
    </div>
  );
}

export default WeeklyCheckInPage;