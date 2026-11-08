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
    "ux_designer": {
        "portfolio": [
            "Write up one case study: the problem, your process, the solution and the result",
            "Add annotated before-and-after screens to your strongest project",
            "Publish or update your portfolio (Behance, Dribbble, Figma or your own site)",
        ],
        "interview_prep": [
            "Practise walking through one portfolio case study out loud, timed",
            "Prepare answers on handling feedback and conflicting stakeholder needs",
            "Review a real product and list 3 usability problems with your suggested fixes",
        ],
    },
    "business_analyst": {
        "portfolio": [
            "Document a process you improved: the current state, the problems and the proposed change",
            "Build a sample dashboard or report from a public dataset and explain the insights",
            "Write a short requirements document or set of user stories for a real or imagined project",
        ],
        "interview_prep": [
            "Practise explaining a past analysis from question to recommendation, timed",
            "Work through 2 practice SQL or Excel questions",
            "Prepare a story about handling disagreeing stakeholders (situation, action, result)",
        ],
    },
    "digital_marketer": {
        "portfolio": [
            "Write up a campaign case study with the goal, channel, budget and measured results",
            "Create a content sample: a blog post, an email sequence or a social media calendar",
            "Run a free SEO or analytics audit of a small site and summarise your findings",
        ],
        "interview_prep": [
            "Explain how you would measure the success of one campaign, timed",
            "Prepare examples with real numbers (reach, conversion rate, cost per result)",
            "Review one brand's marketing and prepare 3 improvement ideas",
        ],
    },
    "finance_analyst": {
        "portfolio": [
            "Build a simple budget or three-statement model in Excel and document its assumptions",
            "Write a one-page analysis of a public company with your conclusion",
            "Create a variance analysis example comparing budget and actual results",
        ],
        "interview_prep": [
            "Walk through a simple discounted cash flow valuation out loud, timed",
            "Practise 2 accounting or Excel technical questions",
            "Prepare a story about catching and fixing an error in a financial analysis",
        ],
    },
}


def templates_for(role: str, agent: str, defaults: dict) -> list:
    return ROLE_TASK_OVERRIDES.get(role, {}).get(agent, defaults[agent])