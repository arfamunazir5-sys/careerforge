import re
from app.analysis.schemas import ResumeAnalysisResult

REQUIRED_SECTIONS = ["education", "experience", "projects", "skills"]

ROLE_KEYWORDS = {
    "swe_backend": ["python", "flask", "fastapi", "sql", "rest api", "docker", "git"],
    "data_analyst": ["python", "sql", "excel", "power bi", "statistics", "pandas", "tableau"],
    "frontend_dev": ["javascript", "react", "html", "css", "git", "responsive design"],
}

# Other common ways people write the same skill.
SKILL_ALIASES = {
    "sql": ["mysql", "postgresql", "postgres", "sqlite"],
    "rest api": ["restful"],
    "react": ["reactjs"],
    "power bi": ["powerbi"],
}

ACTION_KEYWORDS = ["led", "built", "developed", "designed", "implemented", "improved", "optimized", "achieved"]


def _contains(text_lower: str, term: str) -> bool:
    """Whole-word match, so 'led' is not found inside 'skilled' and 'git' is not
    found inside 'github'. Allows a plural ending and digits (REST APIs, HTML5)."""
    pattern = r"(?<![a-z])" + re.escape(term) + r"(?:s|es)?(?![a-z])"
    return re.search(pattern, text_lower) is not None


def _has_skill(text_lower: str, skill: str) -> bool:
    return any(_contains(text_lower, t) for t in [skill] + SKILL_ALIASES.get(skill, []))


def analyze_resume(resume_text: str, target_role: str) -> ResumeAnalysisResult:
    text_lower = resume_text.lower()

    role_skills = ROLE_KEYWORDS.get(target_role, [])
    found_skills = [s for s in role_skills if _has_skill(text_lower, s)]
    missing_skills = [s for s in role_skills if not _has_skill(text_lower, s)]

    weak_sections = [s for s in REQUIRED_SECTIONS if s not in text_lower]
    keyword_gaps = [k for k in ACTION_KEYWORDS if not _contains(text_lower, k)]

    skill_ratio = len(found_skills) / len(role_skills) if role_skills else 0.5
    section_ratio = (len(REQUIRED_SECTIONS) - len(weak_sections)) / len(REQUIRED_SECTIONS)
    keyword_ratio = (len(ACTION_KEYWORDS) - len(keyword_gaps)) / len(ACTION_KEYWORDS)

    resume_score = round((skill_ratio * 0.5 + section_ratio * 0.3 + keyword_ratio * 0.2) * 100)

    return ResumeAnalysisResult(
        resume_score=resume_score,
        missing_skills=missing_skills,
        weak_sections=weak_sections,
        keyword_gaps=keyword_gaps,
    )