"""Single list of supported target roles and their display names."""

ROLE_LABELS = {
    "swe_backend": "Backend Developer",
    "data_analyst": "Data Analyst",
    "frontend_dev": "Frontend Developer",
    "ml_engineer": "AI/ML Engineer",
    "cloud_devops": "Cloud / DevOps Engineer",
    "cybersecurity": "Cybersecurity Analyst",
}


def role_options() -> list:
    return [{"value": key, "label": label} for key, label in ROLE_LABELS.items()]