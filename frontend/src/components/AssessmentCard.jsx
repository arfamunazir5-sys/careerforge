import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import "./Phase2.css";

function AssessmentCard({ refreshKey }) {
  const [state, setState] = useState(null);

  useEffect(() => {
    api.getState().then(setState).catch(() => setState(null));
  }, [refreshKey]);

  if (!state) return null;

  const a = state.assessment || {};
  const taken = Boolean(a.interview || a.networking || a.confidence !== undefined);

  if (!taken) {
    return (
      <Card
        title="Self-assessment"
        subtitle="Interview, networking and confidence are sample values until you answer"
      >
        <p className="p2-text">
          A short quiz and a few questions replace those sample numbers with your own, so the agents
          bid on what you actually need.
        </p>
        <div style={{ marginTop: "var(--cf-space-3)" }}>
          <Link className="btn-primary" to="/assessment">
            Take the 3-minute assessment
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <Card title="Self-assessment" subtitle="Your own answers, used by the Interview and Networking agents">
      <div className="p2-chips">
        {a.interview && (
          <Badge tone="primary">{`Interview quiz ${a.interview.correct}/${a.interview.total}`}</Badge>
        )}
        {a.networking && <Badge tone="primary">{`Networking check ${a.networking.score}`}</Badge>}
        {a.confidence !== undefined && <Badge tone="primary">{`Confidence ${a.confidence}/10`}</Badge>}
      </div>
      {a.interview && a.interview.missed_topics && a.interview.missed_topics.length > 0 && (
        <>
          <p className="p2-label">Topics to review</p>
          <div className="p2-chips">
            {a.interview.missed_topics.map((t) => (
              <Badge key={t} tone="warning">{t}</Badge>
            ))}
          </div>
        </>
      )}
      <div style={{ marginTop: "var(--cf-space-3)" }}>
        <Link className="btn-secondary" to="/assessment">
          Retake
        </Link>
      </div>
    </Card>
  );
}

export default AssessmentCard;