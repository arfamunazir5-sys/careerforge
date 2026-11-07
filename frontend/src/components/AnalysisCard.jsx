import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import "./Phase2.css";
import { ROLE_LABELS } from "../roles";

function AnalysisCard({ refreshKey }) {
  const [state, setState] = useState(null);

  useEffect(() => {
    api.getState().then(setState).catch(() => setState(null));
  }, [refreshKey]);

  if (!state) return null;

  const resume =
    state.resume_details && state.resume_details.missing_skills ? state.resume_details : null;
  const repo =
    state.portfolio_details && state.portfolio_details.repo_count !== undefined
      ? state.portfolio_details
      : null;

  if (!resume && !repo) {
    return (
      <Card title="Profile analysis" subtitle="What CareerForge found in your resume and GitHub">
        <p className="p2-text">
          No resume or GitHub analysis yet. <Link to="/profile">Add them on the Profile page</Link>{" "}
          to see your missing skills and portfolio findings here.
        </p>
      </Card>
    );
  }

  const roleLabel = resume ? ROLE_LABELS[resume.role] || resume.role : "";

  return (
    <Card
      title="Profile analysis"
      subtitle="What CareerForge found in the resume and GitHub profile you provided"
    >
      {resume && (
        <div className="p2-block">
          <div className="p2-block-head">
            <strong>Resume</strong>
            <Badge tone="primary">{`Score ${state.resume_score}`}</Badge>
          </div>
          {resume.missing_skills.length === 0 ? (
            <Badge tone="success">{`Covers the key skills for ${roleLabel}`}</Badge>
          ) : (
            <>
              <p className="p2-label">{`Missing for ${roleLabel}`}</p>
              <div className="p2-chips">
                {resume.missing_skills.map((s) => (
                  <Badge key={s} tone="warning">{s}</Badge>
                ))}
              </div>
            </>
          )}
          {resume.weak_sections && resume.weak_sections.length > 0 && (
            <>
              <p className="p2-label">Sections not found</p>
              <div className="p2-chips">
                {resume.weak_sections.map((s) => (
                  <Badge key={s}>{s}</Badge>
                ))}
              </div>
            </>
          )}
          {resume.keyword_gaps && resume.keyword_gaps.length > 0 && (
            <>
              <p className="p2-label">Action words not used</p>
              <div className="p2-chips">
                {resume.keyword_gaps.map((s) => (
                  <Badge key={s}>{s}</Badge>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {repo && (
        <div className="p2-block">
          <div className="p2-block-head">
            <strong>GitHub</strong>
            <Badge tone="primary">{`Score ${state.portfolio_score}`}</Badge>
          </div>
          <p className="p2-text">
            {repo.repo_count} original public {repo.repo_count === 1 ? "repository" : "repositories"},{" "}
            {Math.round((repo.readme_ratio || 0) * 100)}% with a description.
          </p>
          {repo.notes && repo.notes.length > 0 && (
            <ul className="p2-list">
              {repo.notes.map((n) => (
                <li key={n}>{n}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </Card>
  );
}

export default AnalysisCard;