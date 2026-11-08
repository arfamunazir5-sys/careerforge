"""Single list of supported target roles, their display names and how their
portfolio is assessed ("github" scans repositories, "evidence" uses links and a checklist)."""

ROLE_LABELS = {
    "swe_backend": "Backend Developer",
    "data_analyst": "Data Analyst",
    "frontend_dev": "Frontend Developer",
    "ml_engineer": "AI/ML Engineer",
    "cloud_devops": "Cloud / DevOps Engineer",
    "cybersecurity": "Cybersecurity Analyst",
    "ux_designer": "UI/UX Designer",
    "business_analyst": "Business Analyst",
    "digital_marketer": "Digital Marketing Specialist",
    "finance_analyst": "Finance Analyst",
}

ROLE_PORTFOLIO_MODE = {
    "swe_backend": "github",
    "data_analyst": "github",
    "frontend_dev": "github",
    "ml_engineer": "github",
    "cloud_devops": "github",
    "cybersecurity": "github",
    "ux_designer": "evidence",
    "business_analyst": "evidence",
    "digital_marketer": "evidence",
    "finance_analyst": "evidence",
}

# Used when a role change switches the kind of portfolio evidence: a GitHub score and
# an evidence score are not comparable, so the score goes back to the neutral start value.
NEUTRAL_PORTFOLIO_SCORE = 50


def portfolio_mode(role: str) -> str:
    return ROLE_PORTFOLIO_MODE.get(role, "github")


def role_options() -> list:
    return [
        {"value": key, "label": label, "portfolio_mode": portfolio_mode(key)}
        for key, label in ROLE_LABELS.items()
    ]