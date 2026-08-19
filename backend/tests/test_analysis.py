from app.analysis.resume_analyzer import analyze_resume
from app.analysis.skill_graph import get_next_skill, get_full_chain


def test_resume_analyzer_scores_reasonably():
    resume_text = """
    Education
    Bachelor of Computer Applications

    Experience
    Built and developed a REST API using Python and FastAPI.
    Implemented database integration using SQL.

    Projects
    Created a portfolio project using Git.

    Skills
    Python, FastAPI, SQL, Git
    """
    result = analyze_resume(resume_text, "swe_backend")

    assert 0 <= result.resume_score <= 100
    assert "flask" in result.missing_skills
    assert "docker" in result.missing_skills
    assert result.weak_sections == []
    print(f"resume_score={result.resume_score}, missing={result.missing_skills}")


def test_skill_graph_returns_next_unblocked_skill():
    next_skill = get_next_skill("swe_backend", ["python"])
    assert next_skill == "flask"

    full_chain = get_full_chain("swe_backend")
    assert full_chain[0] == "python"
    assert "docker" in full_chain
    print(f"next_skill={next_skill}, chain={full_chain}")