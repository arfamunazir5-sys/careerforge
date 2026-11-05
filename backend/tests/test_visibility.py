"""Phase 2 tests: shares, share shifts, profile flag, stored analysis details,
honest explanation wording."""
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate, compute_shares
from app.state.schemas import StateVector, SkillProgress
import app.analysis.portfolio_scanner as portfolio_scanner


def state(c):
    return c.get("/state").json()


def dashboard(c):
    body = c.get("/dashboard").json()
    return body[0] if isinstance(body, list) else body


def make_state(**over):
    base = dict(
        user_id="t", target_role="frontend_dev", week_number=1, available_hours=15,
        completed_tasks_last_week=0, ignored_tasks_last_week=0, confidence=6,
        interview_score=61, resume_score=60, networking_score=43, portfolio_score=53,
        streak_count=2, skill_progress=SkillProgress(completed_skills=[], next_skill="html_css"),
    )
    base.update(over)
    return StateVector(**base)


def bids_for(s):
    return [m.get_bid(s) for m in (skill_agent, networking_agent, portfolio_agent, interview_agent)]


def test_shares_sum_to_100_and_match_whole_hours():
    for hours in (5, 10, 15, 21):
        s = make_state(available_hours=hours)
        bids = bids_for(s)
        shares = compute_shares(s, bids)
        assert abs(sum(shares.values()) - 100) < 0.5
        for a in allocate(s, bids).allocations:
            assert abs(a.hours - shares[a.agent] / 100 * hours) < 1.0


def test_dashboard_exposes_shares_and_share_shifts_key(client):
    client.post("/generate-plan")
    d = dashboard(client)
    assert set(d["allocation_shares"]) == {"skill_building", "networking", "portfolio", "interview_prep"}
    assert d["adaptation"]["share_shifts"] == []


def test_share_shift_appears_after_progress_even_if_hours_do_not_change(client):
    client.post("/generate-plan")
    hours_before = {a["agent"]: a["hours"] for a in dashboard(client)["allocation"]["allocations"]}
    task = next(t for t in client.get("/plan").json()["tasks"] if t["agent"] == "networking")
    client.post(f"/tasks/{task['id']}/complete")
    d = dashboard(client)
    hours_after = {a["agent"]: a["hours"] for a in d["allocation"]["allocations"]}
    assert hours_after == hours_before                      # whole hours did not move
    shifts = {s["agent"]: s for s in d["adaptation"]["share_shifts"]}
    assert shifts["networking"]["change"] < 0               # but the share did


def test_share_shifts_hidden_when_budget_changes(client):
    client.post("/generate-plan")
    task = next(t for t in client.get("/plan").json()["tasks"] if t["agent"] == "networking")
    client.post(f"/tasks/{task['id']}/complete")
    client.post("/update-profile", json={"target_role": "swe_backend", "available_hours": 20})
    assert dashboard(client)["adaptation"]["share_shifts"] == []


def test_profile_completed_flag(client):
    assert state(client)["profile_completed"] is False
    client.post("/update-profile", json={"target_role": "swe_backend", "available_hours": 10})
    assert state(client)["profile_completed"] is True
    client.post("/reset")
    assert state(client)["profile_completed"] is False


def test_analysis_details_are_stored_and_cleared_on_role_change(client, monkeypatch):
    client.post("/analyze-resume", json={"resume_text": "python flask", "target_role": "swe_backend"})
    d = state(client)["resume_details"]
    assert d["role"] == "swe_backend" and "docker" in d["missing_skills"]
    assert "weak_sections" in d and "keyword_gaps" in d

    class FakeResponse:
        status_code = 200

        def json(self):
            return [{"fork": False, "description": "d"}, {"fork": False, "description": ""}]

    monkeypatch.setattr(portfolio_scanner.requests, "get", lambda *a, **k: FakeResponse())
    client.post("/analyze-portfolio", json={"github_username": "someone"})
    p = state(client)["portfolio_details"]
    assert p["repo_count"] == 2 and p["readme_ratio"] == 0.5 and p["notes"]

    client.post("/update-profile", json={"target_role": "data_analyst", "available_hours": 10})
    s = state(client)
    assert s["resume_details"] == {}
    assert s["portfolio_details"]["repo_count"] == 2        # GitHub data is role-independent


def test_explanations_use_bid_strength_not_fake_requests(client):
    d = dashboard(client)
    for item in d["explanations"]["items"]:
        text = item["explanation"]
        assert "bid strength" in text and "% of your hours" in text
        assert "requested" not in text and "stronger case" not in text


def test_streak_wording_is_not_weeks(client):
    reasons = [b["reason"] for b in dashboard(client)["bids"] if b["agent"] == "skill_building"]
    assert "tasks completed in a row" in reasons[0] and "week streak" not in reasons[0]