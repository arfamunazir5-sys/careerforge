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