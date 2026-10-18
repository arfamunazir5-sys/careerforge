import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import "./PagesV2.css";

const ROLE_OPTIONS = [
  { value: "swe_backend", label: "Backend Developer" },
  { value: "data_analyst", label: "Data Analyst" },
  { value: "frontend_dev", label: "Frontend Developer" },
];

const GITHUB_RE = /^(?=.{1,39}$)[A-Za-z0-9]+(-[A-Za-z0-9]+)*$/;

function looksLikeSleepingServer(message) {
  const m = String(message || "").toLowerCase();
  return m.includes("failed to fetch") || m.includes("networkerror") || m.includes("load failed");
}

function ProfilePageV2({ onProfileComplete }) {
  const navigate = useNavigate();
  const [targetRole, setTargetRole] = useState("swe_backend");
  const [availableHours, setAvailableHours] = useState(10);
  const [resumeText, setResumeText] = useState("");
  const [githubUsername, setGithubUsername] = useState("");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const [prefilled, setPrefilled] = useState(false);
  const [touched, setTouched] = useState({});
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const [steps, setSteps] = useState([]);
  const [stepIdx, setStepIdx] = useState(-1);

  // Prefill from saved state so returning to this page shows what you
  // actually chose, not the hardcoded defaults.
  useEffect(() => {
    api.getState()
      .then((s) => {
        if (ROLE_OPTIONS.some((r) => r.value === s.target_role)) {
          setTargetRole(s.target_role);
        }
        setAvailableHours(s.available_hours);
        setPrefilled(true);
      })
      .catch(() => {});
  }, []);

  const working = status === "working";

  const hoursNum = Number(availableHours);
  const errors = {};
  if (availableHours === "" || !Number.isInteger(hoursNum) || hoursNum < 1 || hoursNum > 80) {
    errors.hours = "Enter a whole number of hours between 1 and 80.";
  }
  if (githubUsername.trim() && !GITHUB_RE.test(githubUsername.trim())) {
    errors.github =
      "GitHub usernames use letters, numbers and single hyphens, up to 39 characters.";
  }
  const hasErrors = Object.keys(errors).length > 0;
  const showError = (field) => (touched[field] || submitAttempted) && errors[field];
  const touch = (field) => setTouched((t) => ({ ...t, [field]: true }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitAttempted(true);
    if (hasErrors) return;

    const planned = ["Saving your target role and available hours"];
    if (resumeText.trim()) planned.push("Analyzing your resume");
    if (githubUsername.trim()) planned.push("Scanning your GitHub portfolio");
    planned.push("Generating your first weekly plan");
    setSteps(planned);
    setStepIdx(0);
    setStatus("working");
    setError(null);

    try {
      await api.updateProfile({ target_role: targetRole, available_hours: Number(availableHours) });

      let i = 1;
      if (resumeText.trim()) {
        setStepIdx(i);
        await api.analyzeResume({ resume_text: resumeText, target_role: targetRole });
        i += 1;
      }

      if (githubUsername.trim()) {
        setStepIdx(i);
        await api.analyzePortfolio({ github_username: githubUsername.trim() });
        i += 1;
      }

      setStepIdx(i);
      await api.generatePlan();

      setStepIdx(planned.length);
      if (onProfileComplete) onProfileComplete();
      navigate("/dashboard");
    } catch (err) {
      setStatus("error");
      setError(err.message);
    }
  };

  const stepState = (idx) => {
    if (status === "error" && idx === stepIdx) return "failed";
    if (idx < stepIdx) return "done";
    if (idx === stepIdx) return "active";
    return "pending";
  };

  return (
    <div className="cf-page">
      <div className="pw-header">
        <div>
          <h2 className="pw-title">Tell CareerForge About Yourself</h2>
          <p className="pw-subtitle">
            This becomes the real input to your allocation. Nothing here is hardcoded.
          </p>
        </div>
        {prefilled && <Badge tone="success">Saved settings loaded</Badge>}
      </div>

      <Card>
        <form onSubmit={handleSubmit} noValidate>
          <fieldset className="pf-fieldset" disabled={working}>
            <div className="pf-field">
              <label className="pf-label" htmlFor="pf-role">Target role</label>
              <select
                id="pf-role"
                className="pf-input"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
              >
                {ROLE_OPTIONS.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
              <span className="pf-help">Your role decides how much each agent matters for you.</span>
            </div>

            <div className="pf-field">
              <label className="pf-label" htmlFor="pf-hours">Available hours this week</label>
              <input
                id="pf-hours"
                type="number"
                min="1"
                max="80"
                className={`pf-input ${showError("hours") ? "invalid" : ""}`}
                value={availableHours}
                onChange={(e) => setAvailableHours(e.target.value)}
                onBlur={() => touch("hours")}
              />
              {showError("hours") ? (
                <span className="pf-error">{errors.hours}</span>
              ) : (
                <span className="pf-help">This is the budget the agents compete for.</span>
              )}
            </div>

            <div className="pf-field">
              <label className="pf-label" htmlFor="pf-resume">
                Resume <span className="pf-optional">(paste as text, optional)</span>
              </label>
              <textarea
                id="pf-resume"
                rows="8"
                className="pf-input"
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your resume text here (optional, but improves accuracy)"
              />
              <span className="pf-help">{resumeText.length} characters</span>
            </div>

            <div className="pf-field">
              <label className="pf-label" htmlFor="pf-github">
                GitHub username <span className="pf-optional">(optional)</span>
              </label>
              <input
                id="pf-github"
                type="text"
                className={`pf-input ${showError("github") ? "invalid" : ""}`}
                value={githubUsername}
                onChange={(e) => setGithubUsername(e.target.value)}
                onBlur={() => touch("github")}
                placeholder="octocat"
              />
              {showError("github") ? (
                <span className="pf-error">{errors.github}</span>
              ) : (
                <span className="pf-help">Used to scan your public repositories.</span>
              )}
            </div>

            <button type="submit" className="btn-primary pf-submit" disabled={working}>
              {working ? "Working..." : "Analyze Me & Build My Plan"}
            </button>
          </fieldset>
        </form>

        {steps.length > 0 && (working || status === "error") && (
          <ol className="pf-steps">
            {steps.map((label, idx) => {
              const s = stepState(idx);
              return (
                <li key={label} className={`pf-step ${s}`}>
                  <span className="pf-step-mark">
                    {s === "done" ? "\u2713" : s === "failed" ? "!" : idx + 1}
                  </span>
                  {label}
                </li>
              );
            })}
          </ol>
        )}

        {error && (
          <div className="pw-banner" style={{ marginTop: "var(--cf-space-4)" }}>
            {error}
            {looksLikeSleepingServer(error) && (
              <div className="pf-help" style={{ marginTop: 6 }}>
                The server may be waking up (free hosting sleeps when idle). Wait about 30 seconds and submit again. Your answers are kept.
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}

export default ProfilePageV2;