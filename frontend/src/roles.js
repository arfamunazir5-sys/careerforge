// Frontend copy of the supported roles. The Profile page asks the backend for the
// live list (GET /roles) and falls back to this one. Keep it in sync with backend/app/roles.py.
export const ROLE_OPTIONS = [
  { value: "swe_backend", label: "Backend Developer", portfolio_mode: "github" },
  { value: "data_analyst", label: "Data Analyst", portfolio_mode: "github" },
  { value: "frontend_dev", label: "Frontend Developer", portfolio_mode: "github" },
  { value: "ml_engineer", label: "AI/ML Engineer", portfolio_mode: "github" },
  { value: "cloud_devops", label: "Cloud / DevOps Engineer", portfolio_mode: "github" },
  { value: "cybersecurity", label: "Cybersecurity Analyst", portfolio_mode: "github" },
  { value: "ux_designer", label: "UI/UX Designer", portfolio_mode: "evidence" },
  { value: "business_analyst", label: "Business Analyst", portfolio_mode: "evidence" },
  { value: "digital_marketer", label: "Digital Marketing Specialist", portfolio_mode: "evidence" },
  { value: "finance_analyst", label: "Finance Analyst", portfolio_mode: "evidence" },
];

export const ROLE_LABELS = Object.fromEntries(ROLE_OPTIONS.map((r) => [r.value, r.label]));

export function roleLabel(key) {
  return ROLE_LABELS[key] || String(key || "").replace(/_/g, " ");
}