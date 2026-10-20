import { useEffect, useState } from "react";
import { API_BASE_URL } from "../api/client";
import "../theme.css";
import "./Wake.css";

const SLOW_AFTER_MS = 2500;
const RETRY_EVERY_MS = 4000;
const MAX_ATTEMPTS = 15;

export default function WakeUpBanner() {
  const [waking, setWaking] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let finished = false;

    const slowTimer = setTimeout(() => {
      if (!cancelled && !finished) setWaking(true);
    }, SLOW_AFTER_MS);

    const ping = async (attempt) => {
      try {
        const res = await fetch(`${API_BASE_URL}/`);
        if (!res.ok) throw new Error("not ready");
        finished = true;
        if (!cancelled) {
          setWaking(false);
          setFailed(false);
        }
      } catch {
        if (cancelled) return;
        if (attempt < MAX_ATTEMPTS) {
          setTimeout(() => ping(attempt + 1), RETRY_EVERY_MS);
        } else {
          finished = true;
          setWaking(false);
          setFailed(true);
        }
      }
    };

    ping(1);

    return () => {
      cancelled = true;
      clearTimeout(slowTimer);
    };
  }, []);

  if (!waking && !failed) return null;

  if (failed) {
    return (
      <div className="wake-banner failed" role="alert">
        <span className="wake-text">
          Cannot reach the CareerForge server right now. Check your connection, then refresh.
        </span>
        <button type="button" className="btn-secondary" onClick={() => window.location.reload()}>
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="wake-banner" role="status">
      <span className="wake-dot" aria-hidden="true" />
      <span className="wake-text">
        Waking up the server. The free hosting sleeps when idle, so the first load can take up to a minute.
      </span>
    </div>
  );
}
