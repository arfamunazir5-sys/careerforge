"""Phase 6 tests: follow-through learning (bounded, explainable agent weights)."""
import pytest

from app.agents.learning import (
    AGENTS, MAX_PENALTY, WINDOW, follow_through, multiplier_for, record_outcome,
)


def state(c):
    return c.get("/state").json()


def dashboard(c):
    body = c.get("/dashboard").json()
    return body[0] if isinstance(body, list) else body


def tasks_of(c, agent):
    return [t for t in c.get("/plan").json()["tasks"] if t["agent"] == agent]


def test_no_history_means_no_adjustment():
    assert follow_through([]) == 0.5
    assert multiplier_for([]) == 1.0


def test_ignoring_lowers_the_weight_but_never_below_the_bound():
    one = multiplier_for([0])
    many = multiplier_for([0] * 20)
    assert 1 - MAX_PENALTY <= many < one < 1.0
    assert many >= 0.7


def test_completing_tasks_does_not_boost_by_default():
    assert multiplier_for([1]) == 1.0
    assert multiplier_for([1] * 20) == 1.0


def test_a_boost_is_possible_but_bounded_when_enabled():
    boosted = multiplier_for([1] * 20, max_penalty=0.3, max_boost=0.3)
    assert 1.0 < boosted <= 1.3


def test_one_outcome_never_swings_the_plan():
    assert multiplier_for([0]) >= 0.89       # a single ignored task trims at most about 10%


def test_recovery_after_ignoring():
    history = [0, 0, 0, 0]
    assert multiplier_for(history) < 0.85
    for _ in range(8):
        history = record_outcome({"networking": history}, "networking", True)["networking"]
    assert multiplier_for(history) == 1.0 or multiplier_for(history) > 0.95


def test_outcome_window_is_capped_and_input_is_not_mutated():
    original = {"networking": [1, 0]}
    updated = record_outcome(original, "networking", True)
    assert original == {"networking": [1, 0]} and updated == {"networking": [1, 0, 1]}
    long = {}
    for _ in range(WINDOW + 7):
        long = record_outcome(long, "portfolio", False)
    assert len(long["portfolio"]) == WINDOW


def test_task_outcomes_are_recorded_per_agent(client):
    client.post("/generate-plan")
    net = tasks_of(client, "networking")[0]
    port = tasks_of(client, "portfolio")[0]
    client.post(f"/tasks/{net['id']}/complete")
    client.post(f"/tasks/{port['id']}/ignore")
    outcomes = state(client)["agent_outcomes"]
    assert outcomes == {"networking": [1], "portfolio": [0]}


def test_dashboard_reports_what_was_learned(client):
    client.post("/generate-plan")
    learning = dashboard(client)["agent_learning"]
    assert set(learning) == set(AGENTS)
    assert all(v["multiplier"] == 1.0 and v["total"] == 0 for v in learning.values())
    port = tasks_of(client, "portfolio")[0]
    client.post(f"/tasks/{port['id']}/ignore")
    learning = dashboard(client)["agent_learning"]["portfolio"]
    assert learning["total"] == 1 and learning["followed"] == 0 and learning["multiplier"] < 1.0


def test_repeatedly_ignored_agent_gets_a_smaller_share_and_total_stays_whole(client):
    client.post("/generate-plan")
    before = dashboard(client)["allocation_shares"]["networking"]
    for _ in range(4):
        for t in tasks_of(client, "networking"):
            client.post(f"/tasks/{t['id']}/ignore")
        client.post("/generate-plan")
    d = dashboard(client)
    assert d["allocation_shares"]["networking"] < before
    assert d["agent_learning"]["networking"]["multiplier"] < 1.0
    assert abs(sum(d["allocation_shares"].values()) - 100) < 0.5
    assert sum(a["hours"] for a in d["allocation"]["allocations"]) == 10
    assert d["allocation_shares"]["networking"] > 0          # never starved


def test_completing_tasks_leaves_the_allocation_rule_unchanged(client):
    client.post("/generate-plan")
    before = dashboard(client)["agent_learning"]
    for t in tasks_of(client, "interview_prep"):
        client.post(f"/tasks/{t['id']}/complete")
    after = dashboard(client)["agent_learning"]
    assert after["interview_prep"]["multiplier"] == before["interview_prep"]["multiplier"] == 1.0


def test_explanations_mention_follow_through_only_when_it_applies(client):
    client.post("/generate-plan")
    texts = {i["agent"]: i["explanation"] for i in dashboard(client)["explanations"]["items"]}
    assert all("its weight to x" not in t for t in texts.values())
    port = tasks_of(client, "portfolio")[0]
    client.post(f"/tasks/{port['id']}/ignore")
    texts = {i["agent"]: i["explanation"] for i in dashboard(client)["explanations"]["items"]}
    assert "You completed 0 of its last 1 tasks, which lowered its weight to x0.90." in texts["portfolio"]
    assert "lowered its weight" not in texts["networking"]


def test_role_simulator_stays_consistent_with_learning(client):
    client.post("/generate-plan")
    for t in tasks_of(client, "networking"):
        client.post(f"/tasks/{t['id']}/ignore")
    live = {a["agent"]: a["hours"] for a in client.get("/allocate").json()["allocations"]}
    current = next(s for s in client.get("/simulate-roles").json() if s["is_current"])
    assert current["hours"] == live


def test_reset_forgets_outcomes(client):
    client.post("/generate-plan")
    t = tasks_of(client, "networking")[0]
    client.post(f"/tasks/{t['id']}/ignore")
    client.post("/reset")
    assert state(client)["agent_outcomes"] == {}
    assert all(v["multiplier"] == 1.0 for v in client.get("/dashboard").json()[0]["agent_learning"].values())