import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

const ROLE_OPTIONS = [
  { value: "swe_backend", label: "Backend Developer" },
  { value: "data_analyst", label: "Data Analyst" },
  { value: "frontend_dev", label: "Frontend Developer" },
];

function ProfilePage({ onProfileComplete }) {
  const navigate = useNavigate();
  const [targetRole, setTargetRole] = useState("swe_backend");
  const [availableHours, setAvailableHours] = useState(10);
  const [resumeText, setResumeText] = useState("");
  const [githubUsername, setGithubUsername] = useState("");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const [stepLabel, setStepLabel] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("working");
    setError(null);
    try {
      setStepLabel("Saving your target role and available hours...");
      await api.updateProfile({ target_role: targetRole, available_hours: Number(availableHours) });

      if (resumeText.trim()) {
        setStepLabel("Analyzing your resume...");
        await api.analyzeResume({ resume_text: resumeText, target_role: targetRole });
      }

      if (githubUsername.trim()) {
        setStepLabel("Scanning your GitHub portfolio...");
        await api.analyzePortfolio({ github_username: githubUsername });
      }

      setStepLabel("Generating your first weekly plan...");
      await api.generatePlan();

      if (onProfileComplete) onProfileComplete();
      navigate("/dashboard");
    } catch (err) {
      setStatus("error");
      setError(err.message);
    }
  };

  return (
    <section className="profile-page">
      <h2>Tell CareerForge About Yourself</h2>
      <p className="status-text">
        This becomes the real input to your allocation — nothing here is hardcoded.
      </p>

      <form onSubmit={handleSubmit} className="profile-form">
        <label>
          Target Role
          <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)}>
            {ROLE_OPTIONS.map((r) => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>
        </label>

        <label>
          Available Hours This Week
          <input
            type="number"
            min="1"
            max="80"
            value={availableHours}
            onChange={(e) => setAvailableHours(e.target.value)}
          />
        </label>

        <label>
          Resume (paste as text)
          <textarea
            rows="8"
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste your resume text here (optional, but improves accuracy)"
          />
        </label>

        <label>
          GitHub Username
          <input
            type="text"
            value={githubUsername}
            onChange={(e) => setGithubUsername(e.target.value)}
            placeholder="octocat (optional)"
          />
        </label>

        {error && <p className="error-text">{error}</p>}

        <button type="submit" className="btn-primary" disabled={status === "working"}>
          {status === "working" ? stepLabel : "Analyze Me & Build My Plan"}
        </button>
      </form>
    </section>
  );
}

export default ProfilePage;