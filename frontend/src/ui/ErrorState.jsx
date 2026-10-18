import "../theme.css";
import "./States.css";
import Card from "./Card";

function looksLikeSleepingServer(message) {
  const m = String(message || "").toLowerCase();
  return m.includes("failed to fetch") || m.includes("networkerror") || m.includes("load failed");
}

export default function ErrorState({ message, onRetry }) {
  return (
    <Card accent="var(--cf-danger)">
      <div className="st-center">
        <div className="st-icon error" aria-hidden="true">!</div>
        <h3 className="st-title">Something went wrong</h3>
        <p className="st-message">{message || "We could not load this page."}</p>
        {looksLikeSleepingServer(message) && (
          <p className="st-hint">
            The server may be waking up (free hosting sleeps when idle). Wait about 30 seconds, then try again.
          </p>
        )}
        {onRetry && (
          <button type="button" className="btn-secondary" onClick={onRetry}>
            Try again
          </button>
        )}
      </div>
    </Card>
  );
}