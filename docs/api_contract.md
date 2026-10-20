# CareerForge API Contract

Last updated for v1.2. All modules talk to each other only through these JSON
shapes. If a field changes, update this file in the same commit.

Base URL (local): http://127.0.0.1:8000 - Base URL (live): https://careerforge-backend-lo7f.onrender.com
Interactive docs: /docs

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | / | Health check: `{"status": "CareerForge backend is alive"}` |
| GET | /state | Current state vector |
| POST | /reset | Restore the baseline state: `{"status": "reset", "message": "..."}` |
| POST | /update-profile | Set role and hours, returns the updated state |
| POST | /analyze-resume | Analyse resume text, updates resume_score |
| POST | /analyze-portfolio | Scan GitHub, updates portfolio_score |
| GET | /bids | The four agent bids |
| GET | /allocate | Coordinator allocation |
| POST | /generate-plan | Build and save the weekly plan, snapshot the allocation |
| GET | /plan | Current plan, 404 if none yet |
| GET | /export-calendar | .ics download, 404 if no plan |
| POST | /tasks/{task_id}/complete | Mark a task done |
| POST | /tasks/{task_id}/ignore | Mark a task ignored |
| GET | /rewards | Reward log |
| GET | /dashboard | Everything the Command Center needs |
| GET | /skill-graph/{target_role} | Skill chain for a role |
| GET | /skill-progress | Completed and next skills for the current role |

Allowed roles: `swe_backend`, `data_analyst`, `frontend_dev`.
Agent keys: `skill_building`, `networking`, `portfolio`, `interview_prep`.

## state_vector (GET /state, and the response of POST /update-profile)

```json
{
  "user_id": "u1",
  "target_role": "frontend_dev",
  "week_number": 1,
  "available_hours": 15,
  "completed_tasks_last_week": 8,
  "ignored_tasks_last_week": 1,
  "confidence": 6,
  "interview_score": 61,
  "resume_score": 60,
  "networking_score": 43,
  "portfolio_score": 53,
  "streak_count": 7,
  "skill_progress": { "completed_skills": ["python"], "next_skill": "html_css" },
  "skill_task_progress": 1,
  "resume_notes": "",
  "portfolio_notes": "",
  "plan_snapshot": {
    "scores": { "Resume": 60, "Portfolio": 53, "Networking": 43, "Interview": 55 },
    "allocation": { "skill_building": 5, "networking": 3, "portfolio": 4, "interview_prep": 3 },
    "role": "frontend_dev",
    "hours": 15
  },
  "previous_plan_snapshot": {}
}
```

`skill_task_progress` counts completed skill tasks toward the current skill (3 per skill).
`plan_snapshot` is written by POST /generate-plan; `previous_plan_snapshot` holds the one before it and powers the Adaptation panel.

## bid (GET /bids returns a list of these)

```json
{ "agent": "networking", "bid_score": 0.39, "requested_hours": 2, "reason": "networking score is low, needs attention" }
```

`bid_score` is between 0 and 1. The coordinator only uses `bid_score` and the role weight; `requested_hours` is informational.

## allocation (GET /allocate)

```json
{
  "week_number": 1,
  "allocations": [
    { "agent": "skill_building", "hours": 6 },
    { "agent": "networking", "hours": 3 }
  ]
}
```

The hours always sum to `available_hours`.

## weekly_plan (GET /plan and POST /generate-plan)

```json
{
  "week_number": 1,
  "tasks": [
    { "id": "t1", "agent": "skill_building", "title": "Complete a tutorial/module on html_css", "hours": 2, "status": "pending" }
  ]
}
```

`status` is `pending`, `done` or `ignored`. Tasks carry no date. The calendar export places task N on weekday `N mod 7` (Monday first) at 18:00 for `hours` hours, and the UI's "By day" view uses the same rule.

## task update (POST /tasks/{task_id}/complete and /ignore)

```json
{ "task_id": "t1", "status": "done", "reward": 1.0 }
```

Errors: 404 with `detail` if the task id is unknown or the task was already marked. Completing a task raises the matching domain score by 3 (max 100); every 3 skill_building tasks advance the skill roadmap. Ignoring resets `streak_count` to 0.

## update-profile (POST /update-profile)

Request: `{ "target_role": "frontend_dev", "available_hours": 15 }`. Returns a state_vector.

## resume_analysis (POST /analyze-resume)

Request: `{ "resume_text": "...", "target_role": "swe_backend" }`

```json
{
  "resume_score": 73,
  "missing_skills": ["flask", "docker"],
  "weak_sections": [],
  "keyword_gaps": ["led", "designed"]
}
```

Updates `resume_score` and `resume_notes` in the shared state. Resume score changes only through this endpoint.

## portfolio_scan (POST /analyze-portfolio)

Request: `{ "github_username": "octocat" }`

```json
{
  "portfolio_score": 62,
  "repo_count": 6,
  "readme_ratio": 0.5,
  "notes": ["Portfolio looks reasonably active."]
}
```

Updates `portfolio_score` and `portfolio_notes`. Numbers vary with live GitHub data.

## skill_progress (GET /skill-progress)

```json
{
  "target_role": "frontend_dev",
  "completed_skills": ["python"],
  "next_skill": "html_css",
  "full_chain": ["..."]
}
```

GET /skill-graph/{target_role} returns `{ "target_role": "...", "chain": [...] }`.

## dashboard (GET /dashboard)

Note: this endpoint returns a JSON array containing ONE object (a trailing comma in the route). The frontend client unwraps it with `Array.isArray(data) ? data[0] : data`. Keep that unwrap if you touch either side.

```json
{
  "career_health": {
    "overall_score": 54,
    "modules": [
      { "name": "Resume", "score": 60 },
      { "name": "Portfolio", "score": 53 },
      { "name": "Networking", "score": 43 },
      { "name": "Interview", "score": 61 }
    ]
  },
  "explanations": {
    "week_number": 1,
    "items": [
      { "agent": "skill_building", "hours": 6, "explanation": "Skill Building received 6h this week..." }
    ]
  },
  "biggest_opportunity": { "module": "Networking", "note": "..." },
  "bids": [],
  "allocation": { "week_number": 1, "allocations": [] },
  "adaptation": {
    "progress": [
      { "module": "Networking", "before": 43, "after": 52, "change": 9 }
    ],
    "reallocation": [
      { "agent": "networking", "before": 3, "after": 2, "note": "..." }
    ]
  }
}
```

- `overall_score` is the average of the four module scores.
- `bids` and `allocation` use the shapes above.
- `adaptation.progress` and `adaptation.reallocation` are empty lists unless something really changed since the previous plan.

## rewards (GET /rewards)

Returns the stored reward log: a list of the entries written by task updates (`task_id`, `status`, `reward`).

## GET /export-calendar

Returns a downloadable `.ics` file (`text/calendar`, `careerforge_weekly_plan.ics`) built from the current plan. 404 if no plan exists.

## Allocation rules (summary)

```text
need = clamp((70 - score) / 70, 0.05, 1.0)
combined = bid_score x role_weight, normalised, converted to whole hours
(largest-remainder, so the total equals available_hours)
```

Tuning constants live in `backend/app/agents/calibration.py`.