"""Phase 1 data-integrity tests: failed scans, bad input, reset, stale analysis,
and whole-word resume matching."""
import pytest
import requests

import app.analysis.portfolio_scanner as portfolio_scanner
from app.analysis.resume_analyzer import analyze_resume


def state(c):
    return c.get("/state").json()


def fake_github(monkeypatch, status):
    class FakeResponse:
        status_code = status

        def json(self):
            return []

    monkeypatch.setattr(portfolio_scanner.requests, "get", lambda *a, **k: FakeResponse())


@pytest.mark.parametrize("status,expected", [(403, 502), (429, 502), (500, 502), (404, 404)])
def test_failed_github_scan_does_not_overwrite_portfolio_score(client, monkeypatch, status, expected):
    before = state(client)["portfolio_score"]
    fake_github(monkeypatch, status)
    r = client.post("/analyze-portfolio", json={"github_username": "someone"})
    assert r.status_code == expected
    assert state(client)["portfolio_score"] == before


def test_rate_limit_message_is_clear(client, monkeypatch):
    fake_github(monkeypatch, 403)
    detail = client.post("/analyze-portfolio", json={"github_username": "someone"}).json()["detail"]
    assert "rate limit" in detail


def test_network_error_is_a_502_and_changes_nothing(client, monkeypatch):
    before = state(client)

    def boom(*a, **k):
        raise requests.exceptions.ConnectTimeout("timeout")

    monkeypatch.setattr(portfolio_scanner.requests, "get", boom)
    r = client.post("/analyze-portfolio", json={"github_username": "someone"})
    assert r.status_code == 502
    assert state(client) == before


@pytest.mark.parametrize("name", ["", "   ", "bad name", "a/b", "x" * 40])
def test_invalid_github_usernames_are_rejected(client, name):
    assert client.post("/analyze-portfolio", json={"github_username": name}).status_code == 422


def test_unknown_role_is_rejected_everywhere(client):
    before = state(client)
    r = client.post("/update-profile", json={"target_role": "astronaut", "available_hours": 10})
    assert r.status_code == 422 and "Unknown target role" in r.json()["detail"]
    r = client.post("/analyze-resume", json={"resume_text": "python", "target_role": "astronaut"})
    assert r.status_code == 422
    assert state(client) == before


@pytest.mark.parametrize("hours", [0, -3, 81])
def test_hours_outside_1_to_80_are_rejected(client, hours):
    before = state(client)
    r = client.post("/update-profile", json={"target_role": "swe_backend", "available_hours": hours})
    assert r.status_code == 422
    assert state(client) == before


def test_reset_clears_plan_and_reward_log(client):
    client.post("/generate-plan")
    task = client.get("/plan").json()["tasks"][0]
    client.post(f"/tasks/{task['id']}/complete")
    assert len(client.get("/rewards").json()) == 1
    client.post("/reset")
    assert client.get("/plan").status_code == 404
    assert client.get("/rewards").json() == []
    assert client.get("/export-calendar").status_code == 404


def test_role_change_clears_stale_resume_notes_and_skill_progress(client):
    client.post("/analyze-resume", json={"resume_text": "python", "target_role": "swe_backend"})
    client.post("/generate-plan")
    skill = next(t for t in client.get("/plan").json()["tasks"] if t["agent"] == "skill_building")
    client.post(f"/tasks/{skill['id']}/complete")
    s = state(client)
    assert s["resume_notes"] != "" and s["skill_task_progress"] == 1

    client.post("/update-profile", json={"target_role": "swe_backend", "available_hours": 12})
    s = state(client)
    assert s["resume_notes"] != "" and s["skill_task_progress"] == 1  # same role: kept

    client.post("/update-profile", json={"target_role": "data_analyst", "available_hours": 12})
    s = state(client)
    assert s["resume_notes"] == "" and s["skill_task_progress"] == 0


def test_resume_matching_uses_whole_words():
    r = analyze_resume("I am skilled at digital marketing, github and mysql", "swe_backend")
    assert "git" in r.missing_skills          # not found inside 'digital' or 'github'
    assert "sql" not in r.missing_skills      # MySQL counts as SQL
    assert "led" in r.keyword_gaps            # not found inside 'skilled'


def test_resume_matching_accepts_plurals_digits_and_aliases():
    r = analyze_resume("Built REST APIs with ReactJS and HTML5", "swe_backend")
    assert "rest api" not in r.missing_skills
    f = analyze_resume("ReactJS, HTML5, CSS", "frontend_dev")
    assert "react" not in f.missing_skills and "html" not in f.missing_skills
    assert "built" not in r.keyword_gaps