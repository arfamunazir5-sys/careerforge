# CareerForge Data Contract

Every module talks to every other module only through these exact JSON
shapes. If a field needs to change, post it in the group chat first —
other people's code depends on it.

## state_vector — output of GET /state
Fields: user_id, target_role, week_number, available_hours,
completed_tasks_last_week, ignored_tasks_last_week, confidence,
interview_score, resume_score, networking_score, portfolio_score,
streak_count, skill_progress { completed_skills[], next_skill }

```json
{
  "user_id": "u1",
  "target_role": "swe_backend",
  "week_number": 1,
  "available_hours": 10,
  "completed_tasks_last_week": 3,
  "ignored_tasks_last_week": 1,
  "confidence": 6,
  "interview_score": 55,
  "resume_score": 60,
  "networking_score": 40,
  "portfolio_score": 50,
  "streak_count": 2,
  "skill_progress": {
    "completed_skills": ["python"],
    "next_skill": "flask"
  }
}
## weekly_plan — output of GET /plan (and POST /generate-plan)
```json
{
  "week_number": 1,
  "tasks": [
    { "id": "t1", "agent": "skill_building", "title": "Complete a tutorial/module on flask", "hours": 2, "status": "pending" }
  ]
}
## resume_analysis — output of POST /analyze-resume
Request body: { "resume_text": "...", "target_role": "swe_backend" }
```json
{
  "resume_score": 73,
  "missing_skills": ["flask", "docker"],
  "weak_sections": [],
  "keyword_gaps": ["led", "designed", "improved", "optimized", "achieved"]
}
```
Automatically updates resume_score in the shared state.

## portfolio_scan — output of POST /analyze-portfolio
Request body: { "github_username": "octocat" }
```json
{
  "portfolio_score": 62,
  "repo_count": 6,
  "readme_ratio": 0.5,
  "notes": ["Portfolio looks reasonably active."]
}
```
Automatically updates portfolio_score in the shared state. Numbers vary with live GitHub data.

## skill_progress — output of GET /skill-progress
```json
{
  "target_role": "swe_backend",
  "completed_skills": ["python"],
  "next_skill": "flask",
  "full_chain": ["python", "flask", "rest_apis", "databases", "docker", "deployment"]
}
```
Reads live from state — always respects prerequisite order.