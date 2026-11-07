"""Phase 5 tests: weekly check-in (week rollover and history) and per-task reasoning."""
import json
import pytest

import app.plan.plan_store as plan_store
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate
from app.plan.plan_generator import generate_plan
from app.state.schemas import StateVector, SkillProgress


def state(c):
    return c.get("/state").json()


def task_of(c, agent):
    return next(t for t in c.get("/plan").json()["tasks"] if t["agent"] == agent)


def test_week_summary_needs_a_plan(client):
    assert client.get("/week-summary").status_code == 404
    assert client.post("/next-week", json={}).status_code == 404


def test_week_summary_counts_tasks_hours_and_score_changes(client):
    client.post("/generate-plan")
    net = task_of(client, "networking")
    port = task_of(client, "portfolio")
    client.post(f"/tasks/{net['id']}/complete")
    client.post(f"/tasks/{port['id']}/ignore")
    s = client.get("/week-summary").json()
    total = len(client.get("/plan").json()["tasks"])
    assert s["week_number"] == 1 and s["tasks_total"] == total
    assert s["done"] == 1 and s["ignored"] == 1 and s["pending"] == total - 2
    assert s["hours_done"] == net["hours"] and s["hours_total"] == 10
    assert s["completion_pct"] == round(1 / total * 100)
    assert s["score_changes"] == {"Networking": 3}


def test_next_week_rolls_the_week_and_builds_a_fresh_plan(client):
    client.post("/generate-plan")
    net = task_of(client, "networking")
    client.post(f"/tasks/{net['id']}/complete")
    r = client.post("/next-week", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["week_number"] == 2 and body["closed"]["week_number"] == 1 and body["closed"]["done"] == 1
    assert body["plan"]["week_number"] == 2
    assert all(t["status"] == "pending" for t in body["plan"]["tasks"])
    assert sum(t["hours"] for t in body["plan"]["tasks"]) == 10

    s = state(client)
    assert s["week_number"] == 2
    assert s["completed_tasks_last_week"] == 1 and s["ignored_tasks_last_week"] == 0
    assert len(s["week_history"]) == 1 and s["week_history"][0]["week_number"] == 1
    assert s["week_history"][0]["role"] == "swe_backend"
    assert client.get("/plan").json()["week_number"] == 2


def test_closing_twice_keeps_history_in_order(client):
    client.post("/generate-plan")
    client.post("/next-week", json={})
    client.post("/next-week", json={})
    s = state(client)
    assert s["week_number"] == 3
    assert [w["week_number"] for w in s["week_history"]] == [1, 2]


def test_next_week_can_change_hours_and_confidence(client):
    client.post("/generate-plan")
    body = client.post("/next-week", json={"available_hours": 14, "confidence": 9}).json()
    assert sum(t["hours"] for t in body["plan"]["tasks"]) == 14
    s = state(client)
    assert s["available_hours"] == 14 and s["confidence"] == 9


@pytest.mark.parametrize("payload", [{"available_hours": 0}, {"available_hours": 81}, {"confidence": 0}, {"confidence": 11}])
def test_invalid_next_week_requests_change_nothing(client, payload):
    client.post("/generate-plan")
    before = state(client)
    plan_before = client.get("/plan").json()
    assert client.post("/next-week", json=payload).status_code == 422
    assert state(client) == before
    assert client.get("/plan").json() == plan_before


def test_history_is_capped_at_twelve_weeks(client):
    client.post("/generate-plan")
    for _ in range(14):
        client.post("/next-week", json={})
    s = state(client)
    assert s["week_number"] == 15 and len(s["week_history"]) == 12
    assert s["week_history"][0]["week_number"] == 3 and s["week_history"][-1]["week_number"] == 14


def test_reset_clears_weeks_and_history(client):
    client.post("/generate-plan")
    client.post("/next-week", json={})
    client.post("/reset")
    s = state(client)
    assert s["week_number"] == 1 and s["week_history"] == []


def test_every_task_explains_why_it_exists(client):
    tasks = client.post("/generate-plan").json()["tasks"]
    for t in tasks:
        assert "bid strength" in t["why"] and "% of your hours" in t["why"]
    skill = next(t for t in tasks if t["agent"] == "skill_building")
    next_skill = state(client)["skill_progress"]["next_skill"]
    assert f"'{next_skill}'" in skill["why"]


def test_reasoning_survives_marking_tasks_done(client):
    client.post("/generate-plan")
    t = task_of(client, "networking")
    why = t["why"]
    client.post(f"/tasks/{t['id']}/complete")
    assert task_of(client, "networking")["why"] == why


def test_plans_saved_before_this_feature_still_load(client, tmp_path):
    old = {"week_number": 1, "tasks": [{"id": "t1", "agent": "networking", "title": "x", "hours": 2, "status": "pending"}]}
    with open(plan_store.PLAN_PATH, "w") as f:
        json.dump(old, f)
    assert client.get("/plan").json()["tasks"][0]["why"] == ""


def test_generate_plan_still_works_without_reasoning():
    s = StateVector(
        user_id="t", target_role="swe_backend", week_number=1, available_hours=10,
        completed_tasks_last_week=0, ignored_tasks_last_week=0, confidence=6,
        interview_score=55, resume_score=60, networking_score=40, portfolio_score=50, streak_count=0,
        skill_progress=SkillProgress(completed_skills=["python"], next_skill="flask"),
    )
    bids = [m.get_bid(s) for m in (skill_agent, networking_agent, portfolio_agent, interview_agent)]
    plan = generate_plan(s, allocate(s, bids))
    assert plan.tasks
    assert all(t.why == "" or t.why.startswith("This task targets") for t in plan.tasks)