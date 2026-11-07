import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { assessmentApi } from "../api/assessment";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import ErrorState from "../ui/ErrorState";
import { SkeletonCard } from "../ui/Skeleton";
import "../components/Phase2.css";
import "../components/Phase3.css";
import "./PagesV2.css";
import { ROLE_LABELS } from "../roles";

function QuestionBlock({ question, name, value, onChange }) {
  return (
    <fieldset className="as-question">
      <legend className="as-prompt">{question.prompt}</legend>
      {question.options.map((option, idx) => (
        <label key={idx} className={`as-option ${value === idx ? "selected" : ""}`}>
          <input
            type="radio"
            name={name}
            checked={value === idx}
            onChange={() => onChange(idx)}
          />
          <span>{option}</span>
        </label>
      ))}
    </fieldset>
  );
}

function AssessmentPage({ onAssessmentComplete }) {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [interview, setInterview] = useState({});
  const [network, setNetwork] = useState({});
  const [confidence, setConfidence] = useState(6);
  const [confidenceTouched, setConfidenceTouched] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    assessmentApi
      .getQuestions()
      .then(setQuestions)
      .catch((err) => setLoadError(err.message));
  }, []);

  if (loadError) {
    return (
      <div className="cf-page">
        <ErrorState message={loadError} onRetry={() => window.location.reload()} />
      </div>
    );
  }

  if (!questions) {
    return (
      <div className="cf-page pw-stack">
        <SkeletonCard lines={4} />
        <SkeletonCard lines={4} />
      </div>
    );
  }

  const roleLabel = ROLE_LABELS[questions.role] || questions.role;
  const iTotal = questions.interview.length;
  const nTotal = questions.networking.length;
  const iCount = Object.keys(interview).length;
  const nCount = Object.keys(network).length;
  const iPartial = iCount > 0 && iCount < iTotal;
  const nPartial = nCount > 0 && nCount < nTotal;
  const hasSomething = iCount === iTotal || nCount === nTotal || confidenceTouched;
  const canSubmit = hasSomething && !iPartial && !nPartial && !submitting;

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    const payload = {};
    if (iCount === iTotal) payload.interview_answers = interview;
    if (nCount === nTotal) payload.networking_answers = network;
    if (confidenceTouched) payload.confidence = confidence;
    try {
      const summary = await assessmentApi.submit(payload);
      setResult(summary);
      if (onAssessmentComplete) onAssessmentComplete();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRebuild = async () => {
    setRebuilding(true);
    setError(null);
    try {
      await api.generatePlan();
      if (onAssessmentComplete) onAssessmentComplete();
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
      setRebuilding(false);
    }
  };

  if (result) {
    return (
      <div className="cf-page">
        <div className="pw-header">
          <div>
            <h2 className="pw-title">Assessment saved</h2>
            <p className="pw-subtitle">Your answers now drive the agents' bids.</p>
          </div>
        </div>
        <Card>
          {result.interview && (
            <div className="as-result-row">
              <span>
                Interview quiz: {result.interview.correct} of {result.interview.total} correct
              </span>
              <Badge tone="primary">{`Score ${result.interview.score}`}</Badge>
            </div>
          )}
          {result.interview && result.interview.missed_topics.length > 0 && (
            <div style={{ padding: "var(--cf-space-2) 0" }}>
              <p className="p2-label">Topics to review</p>
              <div className="p2-chips">
                {result.interview.missed_topics.map((t) => (
                  <Badge key={t} tone="warning">{t}</Badge>
                ))}
              </div>
            </div>
          )}
          {result.networking && (
            <div className="as-result-row">
              <span>Networking check</span>
              <Badge tone="primary">{`Score ${result.networking.score}`}</Badge>
            </div>
          )}
          {result.confidence !== null && result.confidence !== undefined && (
            <div className="as-result-row">
              <span>Interview confidence</span>
              <Badge tone="primary">{`${result.confidence}/10`}</Badge>
            </div>
          )}
          <p className="pw-note">
            Your Command Center already reflects these results. Rebuild the plan to turn them into new
            tasks. Rebuilding resets this week's done and ignored marks.
          </p>
          {error && <div className="pw-banner" style={{ marginTop: "var(--cf-space-3)" }}>{error}</div>}
          <div className="as-actions">
            <button type="button" className="btn-primary" onClick={handleRebuild} disabled={rebuilding}>
              {rebuilding ? "Rebuilding..." : "Rebuild my plan now"}
            </button>
            <button type="button" className="btn-secondary" onClick={() => navigate("/dashboard")} disabled={rebuilding}>
              Keep my current plan
            </button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="cf-page">
      <div className="pw-header">
        <div>
          <h2 className="pw-title">Self-assessment</h2>
          <p className="pw-subtitle">
            Three short sections for {roleLabel}. Each one is optional, and your answers replace the
            sample values.
          </p>
        </div>
      </div>

      <div className="pw-stack">
        <Card title="Interview quiz" subtitle={`${iTotal} questions for ${roleLabel}`}>
          <p className={`as-progress ${iPartial ? "warn" : ""}`}>
            {iPartial
              ? `Answer all ${iTotal} questions or clear your choices to skip (${iCount} answered)`
              : `${iCount} of ${iTotal} answered`}
          </p>
          {questions.interview.map((q) => (
            <QuestionBlock
              key={q.id}
              question={q}
              name={q.id}
              value={interview[q.id]}
              onChange={(idx) => setInterview((prev) => ({ ...prev, [q.id]: idx }))}
            />
          ))}
          {iCount > 0 && (
            <button type="button" className="btn-secondary" onClick={() => setInterview({})}>
              Clear quiz answers
            </button>
          )}
        </Card>

        <Card title="Networking check" subtitle="About you, not about the quiz">
          <p className={`as-progress ${nPartial ? "warn" : ""}`}>
            {nPartial
              ? `Answer all ${nTotal} questions or clear your choices to skip (${nCount} answered)`
              : `${nCount} of ${nTotal} answered`}
          </p>
          {questions.networking.map((q) => (
            <QuestionBlock
              key={q.id}
              question={q}
              name={q.id}
              value={network[q.id]}
              onChange={(idx) => setNetwork((prev) => ({ ...prev, [q.id]: idx }))}
            />
          ))}
          {nCount > 0 && (
            <button type="button" className="btn-secondary" onClick={() => setNetwork({})}>
              Clear networking answers
            </button>
          )}
        </Card>

        <Card title="Interview confidence" subtitle="1 = not confident at all, 10 = very confident">
          <div className="as-slider-row">
            <input
              className="as-slider"
              type="range"
              min="1"
              max="10"
              value={confidence}
              aria-label="Interview confidence from 1 to 10"
              onChange={(e) => {
                setConfidence(Number(e.target.value));
                setConfidenceTouched(true);
              }}
            />
            <span className="as-slider-value">{confidenceTouched ? `${confidence}/10` : "skip"}</span>
          </div>
        </Card>

        {error && <div className="pw-banner">{error}</div>}

        <button type="button" className="btn-primary pf-submit" onClick={handleSubmit} disabled={!canSubmit}>
          {submitting ? "Saving..." : "Save my assessment"}
        </button>
      </div>
    </div>
  );
}

export default AssessmentPage;