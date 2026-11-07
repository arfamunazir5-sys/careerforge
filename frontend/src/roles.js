// Frontend copy of the supported roles. The Profile page asks the backend for the
// live list (GET /roles) and falls back to this one. Keep it in sync with backend/app/roles.py.
export const ROLE_OPTIONS = [
  { value: "swe_backend", label: "Backend Developer" },
  { value: "data_analyst", label: "Data Analyst" },
  { value: "frontend_dev", label: "Frontend Developer" },
  { value: "ml_engineer", label: "AI/ML Engineer" },
  { value: "cloud_devops", label: "Cloud / DevOps Engineer" },
  { value: "cybersecurity", label: "Cybersecurity Analyst" },
];

export const ROLE_LABELS = Object.fromEntries(ROLE_OPTIONS.map((r) => [r.value, r.label]));

export function roleLabel(key) {
  return ROLE_LABELS[key] || String(key || "").replace(/_/g, " ");
}