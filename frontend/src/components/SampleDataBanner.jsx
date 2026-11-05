import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import "./Phase2.css";

function SampleDataBanner({ refreshKey }) {
  const [state, setState] = useState(null);

  useEffect(() => {
    api.getState().then(setState).catch(() => setState(null));
  }, [refreshKey]);

  if (!state || state.profile_completed !== false) return null;

  return (
    <div className="sd-banner" role="status">
      <span>
        You are viewing sample data. Save your profile so the plan uses your own role, hours and analysis.
      </span>
      <Link className="btn-secondary" to="/profile">
        Complete profile
      </Link>
    </div>
  );
}

export default SampleDataBanner;