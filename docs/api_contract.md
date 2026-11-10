# CareerForge API Contract

Last updated for v2.0. All modules talk to each other only through these JSON
shapes. If a field changes, update this file in the same commit.

Base URL (local): http://127.0.0.1:8000 - Base URL (live): https://careerforge-backend-lo7f.onrender.com
Interactive docs: /docs

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | / | Health check: `{"status": "CareerForge backend is alive"}` |
| GET | /state | Current state vector |
| POST | /reset | Restore the baseline state and delete the weekly plan and reward log: `{"status": "reset", "message": "..."}` |
| POST | /update-profile | Set role and hours, returns the updated state |
| POST | /analyze-resume | Analyse resume text, updates resume_score |
| POST | /analyze-portfolio | Scan GitHub, updates portfolio_score |
| POST | /extract-resume-text | Read the text of an uploaded PDF resume (multipart field `file`); nothing is stored |
| POST | /portfolio-evidence | Score portfolio links and a short checklist for roles without a GitHub portfolio |
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
| GET | /self-assessment/questions | Interview quiz (for the current role) and networking questions, without answers |
| POST | /self-assessment | Score the quiz, networking check and confidence, and update the state |
| GET | /roles | Supported roles: `[{ "value", "label", "portfolio_mode" }]` (`github` or `evidence`) |
| GET | /simulate-roles | Read-only: hours, shares and health score under each role, using current scores |
| GET | /week-summary | Done, ignored and pending tasks, hours and score changes for the current week (404 without a plan) |
| POST | /next-week | Close the current week, advance `week_number`, build a fresh plan |

Allowed roles: `swe_backend`, `data_analyst`, `frontend_dev`, `ml_engineer`, `cloud_devops`, `cybersecurity` (portfolio mode `github`) and `ux_designer`, `business_analyst`, `digital_marketer`, `finance_analyst` (portfolio mode `evidence`). See GET /roles. Every role has its own weights, skill chain, resume keywords, interview quiz and, for portfolio and interview tasks, role-specific task templates.

GET /simulate-roles returns one entry per role: `{ role, label, is_current, hours, shares, health, next_skill }`. It reuses the current scores and hours with each role's weights and skill chain, and never writes state. Resume and quiz results were measured for the current role, so other roles are estimates.
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
  "previous_plan_snapshot": {},
  "profile_completed": false,
  "resume_details": {},
  "portfolio_details": {},
  "assessment": {},
  "week_history": [],
  "agent_outcomes": {}
}
```

`skill_task_progress` counts completed skill tasks toward the current skill (3 per skill).
`profile_completed` is false until POST /update-profile is called (the UI shows a sample-data notice). `resume_details` ({role, missing_skills, weak_sections, keyword_gaps}) and `portfolio_details` ({repo_count, readme_ratio, notes}) store the last analysis for display; a role change clears `resume_details`.
`streak_count` counts tasks completed in a row (not weeks).
`assessment` holds the last self-assessment: `interview` ({role, score, correct, total, missed_topics}), `networking` ({score}) and `confidence` (1-10). A role change clears `assessment.interview`.

## self-assessment (GET /self-assessment/questions, POST /self-assessment)

GET returns `{ "role", "interview": [{id, prompt, options}], "networking": [{id, prompt, options}] }` (no answer key). POST takes any of: `interview_answers` and `networking_answers` (maps of question id to the chosen option index; each section must be fully answered), and `confidence` (1-10).

```json
{ "interview": { "score": 67, "correct": 4, "total": 6, "missed_topics": ["Git basics"] },
  "networking": { "score": 58 }, "confidence": 7 }
```

Scores replace `interview_score` and `networking_score`; confidence replaces `confidence`. Sections not sent are `null`. Errors: 422 for an empty request, a partly answered section, an unknown question id, an invalid option or confidence outside 1-10. The plan snapshot's scores are moved with the new values, so an assessment never appears as task progress.
`plan_snapshot` is written by POST /generate-plan; `previous_plan_snapshot` holds the one before it and powers the Adaptation panel.

## bid (GET /bids returns a list of these)

```json
{ "agent": "networking", "bid_score": 0.39, "requested_hours": 2, "reason": "networking score is low, needs attention" }
```

`bid_score` is between 0 and 1. The coordinator uses `bid_score`, the role weight and the follow-through weight; `requested_hours` is informational and is not shown to users.

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
    { "id": "t1", "agent": "skill_building", "title": "Complete a tutorial/module on html_css", "hours": 2, "status": "pending", "why": "Skill Building received 4h this week. ..." }
  ]
}
```

`status` is `pending`, `done` or `ignored`. `why` is the reasoning captured when the plan was built (empty for plans saved before it existed).

GET /week-summary returns `{ week_number, tasks_total, done, ignored, pending, hours_total, hours_done, completion_pct, score_changes }`. POST /next-week takes optional `available_hours` (1-80) and `confidence` (1-10), appends the closed week to `week_history` (last 12 weeks), advances `week_number`, sets `completed_tasks_last_week` and `ignored_tasks_last_week` to the closed week's counts, builds a fresh plan and returns `{ closed, week_number, plan }`. Pending tasks are not carried over. Tasks carry no date. The calendar export places task N on weekday `N mod 7` (Monday first) at 18:00 for `hours` hours, and the UI's "By day" view uses the same rule.

## task update (POST /tasks/{task_id}/complete and /ignore)

```json
{ "task_id": "t1", "status": "done", "reward": 15 }
```

Errors: 404 with `detail` if the task id is unknown or the task was already marked. Completing a task raises the matching domain score by 3 (max 100); every 3 skill_building tasks advance the skill roadmap. Ignoring resets `streak_count` to 0. Rewards: done = 5, done while `streak_count` >= 1 = 15, ignored = -5. Rewards are only logged (GET /rewards); they do not change future allocations.

## update-profile (POST /update-profile)

Request: `{ "target_role": "frontend_dev", "available_hours": 15 }`. Returns a state_vector. Errors: 422 if `target_role` is not one of the allowed roles or `available_hours` is outside 1-80. Changing the role clears `resume_notes` and `skill_task_progress`.

## extract-resume-text (POST /extract-resume-text)

Multipart upload with one field, `file`, a text-based PDF of at most 2 MB. The first 10 pages are read in memory; the file and the text are never stored. The Profile page puts the returned text into the resume box so the user can check it before analysis.

```json
{ "text": "Education ...", "pages": 1, "chars": 1840, "truncated": false }
```

Errors: 422 for an empty file, a file that is not a PDF, a damaged or password-protected PDF, or a PDF with no extractable text (scanned images); 413 above 2 MB. `truncated` is true when pages or characters (20,000) were cut off.

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

## portfolio_evidence (POST /portfolio-evidence)

For roles whose `portfolio_mode` is `evidence` (GitHub does not apply). Request: `{ "links": ["behance.net/me"], "case_studies": 3, "has_results": true, "has_process": true, "recent_work": false }`.

```json
{ "score": 83, "notes": ["Add something from the last 6 months"],
  "links": [{ "url": "https://behance.net/me", "platform": "Behance", "recognized": true }],
  "case_studies": 3, "has_results": true, "has_process": true, "recent_work": false }
```

Score (0-100): links up to 25 (3 links for full marks), case studies up to 40 (4 for full marks), measurable results 15, process explained 10, recent work 10. Links are normalised, de-duplicated and checked for format and known platform; they are never opened, so the score is self-reported evidence. Updates `portfolio_score`, `portfolio_notes` and `portfolio_details` (`mode: "evidence"`). Errors: 422 for more than 5 links, a malformed link, case studies outside 0-20, or a role that uses the GitHub scan. POST /analyze-portfolio answers 422 for evidence roles. Changing between a `github` and an `evidence` role clears the portfolio details and sets the portfolio score back to 50.

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

Updates `portfolio_score` and `portfolio_notes`. Numbers vary with live GitHub data. `readme_ratio` is the share of original repos that have a GitHub description (READMEs and commits are not checked). Errors: 422 for a blank or invalid username, 404 if the GitHub user does not exist, 502 on a GitHub rate limit or network failure. A failed scan never changes the stored score.

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
  "allocation_shares": { "skill_building": 38.4, "networking": 19.1, "portfolio": 24.5, "interview_prep": 18.0 },
  "agent_learning": { "networking": { "multiplier": 0.9, "followed": 0, "total": 1, "rate": 0.33 } },
  "adaptation": {
    "progress": [
      { "module": "Networking", "before": 43, "after": 52, "change": 9 }
    ],
    "reallocation": [
      { "agent": "networking", "before": 3, "after": 2, "note": "..." }
    ],
    "share_shifts": [
      { "agent": "networking", "before": 19.1, "after": 17.6, "change": -1.5 }
    ]
  }
}
```

- `overall_score` is role-weighted: each module is multiplied by the target role's agent weight (Resume uses the skill_building weight) and the results are summed.
- `bids` and `allocation` use the shapes above. `allocation_shares` is each agent's unrounded share of the week in percent (same math as the allocation, before whole-hour rounding).
- `adaptation.share_shifts` compares the live shares with the shares stored when the current plan was built (changes of 0.1 points or more; empty if the role or hours changed).
- `agent_learning` is each agent's follow-through: `{ multiplier, followed, total, rate }` from its last 20 completed or ignored tasks (`state.agent_outcomes`, 1 = completed, 0 = ignored). The coordinator computes bid x role weight x `multiplier`. The multiplier is 1.0 until tasks are ignored, never below 0.7, and completing tasks does not boost an agent. A smoothed rate (Beta(1,1) prior) keeps a single outcome from swinging the plan.
- `adaptation.progress` and `adaptation.reallocation` are empty lists unless something really changed since the previous plan.

## rewards (GET /rewards)

Returns the stored reward log: a list of the entries written by task updates (`task_id`, `status`, `reward`).

## GET /export-calendar

Returns a downloadable `.ics` file (`text/calendar`, `careerforge_weekly_plan.ics`) built from the current plan. 404 if no plan exists.

## Allocation rules (summary)

```text
need = clamp((70 - score) / 70, 0.05, 1.0)
combined = bid_score x role_weight x follow-through weight, normalised, converted to whole hours
(largest-remainder, so the total equals available_hours)
```

Tuning constants live in `backend/app/agents/calibration.py`.