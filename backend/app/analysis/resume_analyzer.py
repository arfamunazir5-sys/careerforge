from app.analysis.schemas import ResumeAnalysisResult

REQUIRED_SECTIONS = ["education", "experience", "projects", "skills"]

ROLE_KEYWORDS = {
    "swe_backend": ["python", "flask", "fastapi", "sql", "rest api", "docker", "git"],
    "data_analyst": ["python", "sql", "excel", "power bi", "statistics", "pandas", "tableau"],
    "frontend_dev": ["javascript", "react", "html", "css", "git", "responsive design"],
}

ACTION_KEYWORDS = ["led", "built", "developed", "designed", "implemented", "improved", "optimized", "achieved"]


def analyze_resume(resume_text: str, target_role: str) -> ResumeAnalysisResult:
    text_lower = resume_text.lower()

    role_skills = ROLE_KEYWORDS.get(target_role, [])
    found_skills = [s for s in role_skills if s in text_lower]
    missing_skills = [s for s in role_skills if s not in text_lower]

    weak_sections = [s for s in REQUIRED_SECTIONS if s not in text_lower]
    keyword_gaps = [k for k in ACTION_KEYWORDS if k not in text_lower]

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