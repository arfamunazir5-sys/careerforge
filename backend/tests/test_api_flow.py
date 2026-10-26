"""Safety-net tests for the API flow. They pin behaviour that works today so
later fixes cannot silently break it. All files used are in a temp folder."""
import app.analysis.portfolio_scanner as portfolio_scanner


def state(c):
    return c.get("/state").json()


def dashboard(c):
    body = c.get("/dashboard").json()
    return body[0] if isinstance(body, list) else body


def task_of(c, agent):
    return next(t for t in c.get("/plan").json()["tasks"] if t["agent"] == agent)


def test_health_check(client):
    assert client.get("/").json() == {"status": "CareerForge backend is alive"}


def test_plan_is_404_before_generation_and_calendar_too(client):
    assert client.get("/plan").status_code == 404
    assert client.get("/export-calendar").status_code == 404


def test_generate_plan_uses_full_budget_and_stores_snapshot(client):
    plan = client.post("/generate-plan").json()
    s = state(client)
    assert sum(t["hours"] for t in plan["tasks"]) == s["available_hours"]
    assert all(t["status"] == "pending" for t in plan["tasks"])
    assert sum(s["plan_snapshot"]["allocation"].values()) == s["available_hours"]


def test_calendar_export_after_plan(client):
    client.post("/generate-plan")
    r = client.get("/export-calendar")
    assert r.status_code == 200
    assert "text/calendar" in r.headers["content-type"]
    assert r.text.startswith("BEGIN:VCALENDAR")


def test_update_profile_sets_role_hours_and_next_skill(client):
    r = client.post("/update-profile", json={"target_role": "data_analyst", "available_hours": 12})
    assert r.status_code == 200
    s = state(client)
    assert s["target_role"] == "data_analyst"
    assert s["available_hours"] == 12
    assert s["skill_progress"]["next_skill"] == "sql"


def test_reset_restores_baseline_state(client):
    client.post("/update-profile", json={"target_role": "data_analyst", "available_hours": 20})
    assert client.post("/reset").json()["status"] == "reset"
    s = state(client)
    assert s["target_role"] == "swe_backend"
    assert s["available_hours"] == 10


def test_completing_a_networking_task(client):
    client.post("/generate-plan")
    before = state(client)
    t = task_of(client, "networking")
    r = client.post(f"/tasks/{t['id']}/complete")
    assert r.status_code == 200
    assert r.json() == {"task_id": t["id"], "status": "done", "reward": 15}
    after = state(client)
    assert after["networking_score"] == before["networking_score"] + 3
    assert after["streak_count"] == before["streak_count"] + 1
    assert after["completed_tasks_last_week"] == before["completed_tasks_last_week"] + 1
    assert after["resume_score"] == before["resume_score"]


def test_ignoring_a_task_resets_streak_and_gives_negative_reward(client):
    client.post("/generate-plan")
    before = state(client)
    t = task_of(client, "portfolio")
    r = client.post(f"/tasks/{t['id']}/ignore")
    assert r.json()["reward"] == -5
    after = state(client)
    assert after["streak_count"] == 0
    assert after["ignored_tasks_last_week"] == before["ignored_tasks_last_week"] + 1
    assert after["portfolio_score"] == before["portfolio_score"]


def test_task_cannot_be_marked_twice_and_unknown_task_is_404(client):
    client.post("/generate-plan")
    t = task_of(client, "interview_prep")
    assert client.post(f"/tasks/{t['id']}/complete").status_code == 200
    again = client.post(f"/tasks/{t['id']}/complete")
    assert again.status_code == 404
    assert "already been marked" in again.json()["detail"]
    assert client.post("/tasks/nope/complete").status_code == 404


def test_rewards_log_records_each_update(client):
    client.post("/generate-plan")
    a = task_of(client, "networking")
    b = task_of(client, "portfolio")
    client.post(f"/tasks/{a['id']}/complete")
    client.post(f"/tasks/{b['id']}/ignore")
    log = client.get("/rewards").json()
    assert [e["status"] for e in log] == ["done", "ignored"]


def test_skill_tasks_advance_the_roadmap_after_three(client):
    start = state(client)["skill_progress"]["next_skill"]
    for _ in range(3):  # each plan has only 2 skill tasks at the baseline budget
        client.post("/generate-plan")
        for t in client.get("/plan").json()["tasks"]:
            if t["agent"] == "skill_building":
                client.post(f"/tasks/{t['id']}/complete")
        if state(client)["skill_progress"]["next_skill"] != start:
            break
    s = state(client)
    assert start in s["skill_progress"]["completed_skills"]
    assert s["skill_progress"]["next_skill"] != start


def test_dashboard_shape_and_adaptation_progress(client):
    client.post("/generate-plan")
    d = dashboard(client)
    for key in ("career_health", "explanations", "biggest_opportunity", "bids", "allocation", "adaptation"):
        assert key in d
    assert len(d["bids"]) == 4
    assert d["adaptation"]["progress"] == []
    t = task_of(client, "networking")
    client.post(f"/tasks/{t['id']}/complete")
    progress = dashboard(client)["adaptation"]["progress"]
    assert [(p["module"], p["change"]) for p in progress] == [("Networking", 3)]


def test_analyze_resume_updates_state(client):
    text = "Education Experience Projects Skills python sql git built developed"
    r = client.post("/analyze-resume", json={"resume_text": text, "target_role": "swe_backend"})
    assert r.status_code == 200
    s = state(client)
    assert s["resume_score"] == r.json()["resume_score"]
    assert s["resume_notes"].startswith("Missing from resume:")


def test_analyze_portfolio_success_updates_state(client, monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return [{"fork": False, "description": "d"} for _ in range(4)]

    monkeypatch.setattr(portfolio_scanner.requests, "get", lambda *a, **k: FakeResponse())
    r = client.post("/analyze-portfolio", json={"github_username": "someone"})
    assert r.status_code == 200
    assert r.json()["repo_count"] == 4
    assert state(client)["portfolio_score"] == r.json()["portfolio_score"]