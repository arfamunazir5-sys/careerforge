"""Role-specific task templates. Roles or agents not listed here use the default
templates in plan_generator.py (skill_building always uses {next_skill})."""

ROLE_TASK_OVERRIDES = {
    "data_analyst": {
        "interview_prep": [
            "Write and explain 2 SQL queries on a practice dataset",
            "Do one mock interview question out loud: walk through an analysis from question to insight",
            "Review how you would explain a chart or finding to a non-technical audience",
        ],
    },
    "ml_engineer": {
        "portfolio": [
            "Write a clear README for your best ML project, with results and how to run it",
            "Push a notebook or experiment with a clean, reproducible setup",
            "Publish a trained model or demo (Streamlit, a Hugging Face Space or a simple API)",
        ],
        "interview_prep": [
            "Explain bias, variance and overfitting out loud, timed",
            "Work through 2 practice questions on model evaluation metrics",
            "Review how you would explain one of your projects end to end",
        ],
    },
    "cloud_devops": {
        "portfolio": [
            "Document a project with an architecture diagram and a README",
            "Add a CI pipeline (for example GitHub Actions) to one of your repositories",
            "Deploy a small app to a cloud provider and write down the steps",
        ],
        "interview_prep": [
            "Explain containers, images and orchestration out loud, timed",
            "Troubleshoot a practice Linux or networking scenario step by step",
            "Review how you would design a simple deployment pipeline",
        ],
    },
    "cybersecurity": {
        "portfolio": [
            "Write up a CTF challenge or lab you solved, with your method and what you learned",
            "Publish a small security tool or script with a clear README",
            "Document a home-lab or secure-configuration exercise step by step",
        ],
        "interview_prep": [
            "Explain the CIA triad and a real attack example out loud, timed",
            "Work through 2 practice questions on common web vulnerabilities (OWASP Top 10)",
            "Review how you would respond to a security incident, step by step",
        ],
    },
}


def templates_for(role: str, agent: str, defaults: dict) -> list:
    return ROLE_TASK_OVERRIDES.get(role, {}).get(agent, defaults[agent])