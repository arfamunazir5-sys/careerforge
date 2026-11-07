"""Phase 4 tests: every supported role is fully wired, and the role simulator is read-only."""
import json
import pytest

from app.agents.role_weights import ROLE_WEIGHTS
from app.analysis.resume_analyzer import ROLE_KEYWORDS
from app.analysis.self_assessment import INTERVIEW_BANK
from app.analysis.skill_graph import get_full_chain
from app.roles import ROLE_LABELS

ROLES = list(ROLE_LABELS)
AGENTS = {"skill_building", "networking", "portfolio", "interview_prep"}


def state(c):
    return c.get("/state").json()


def test_registry_matches_every_role_table():
    assert set(ROLE_LABELS) == set(ROLE_WEIGHTS) == set(ROLE_KEYWORDS) == set(INTERVIEW_BANK)
    assert len(ROLES) == 6


@pytest.mark.parametrize("role", ROLES)
def test_role_has_complete_configuration(role):
    weights = ROLE_WEIGHTS[role]
    assert set(weights) == AGENTS and abs(sum(weights.values()) - 1.0) < 1e-9
    chain = get_full_chain(role)
    assert len(chain) >= 5 and len(chain) == len(set(chain))
    assert len(ROLE_KEYWORDS[role]) >= 6
    assert len(INTERVIEW_BANK[role]) >= 6


def test_roles_endpoint_lists_every_role(client):
    data = client.get("/roles").json()
    assert [r["value"] for r in data] == ROLES
    assert all(r["label"] for r in data)


@pytest.mark.parametrize("role", ROLES)
def test_role_works_end_to_end(client, role):
    r = client.post("/update-profile", json={"target_role": role, "available_hours": 12})
    assert r.status_code == 200
    assert state(client)["skill_progress"]["next_skill"] in get_full_chain(role)

    bids = client.get("/bids").json()
    assert {b["agent"] for b in bids} == AGENTS and all(0 <= b["bid_score"] <= 1 for b in bids)
    allocation = client.get("/allocate").json()["allocations"]
    assert sum(a["hours"] for a in allocation) == 12

    plan = client.post("/generate-plan").json()
    assert sum(t["hours"] for t in plan["tasks"]) == 12
    assert {t["agent"] for t in plan["tasks"]} <= AGENTS
    assert all("DSA" not in t["title"] for t in plan["tasks"] if role != "swe_backend" and role != "frontend_dev")

    resume = client.post("/analyze-resume", json={"resume_text": "Education Experience Projects Skills", "target_role": role})
    assert resume.status_code == 200
    assert set(resume.json()["missing_skills"]) == set(ROLE_KEYWORDS[role])

    quiz = client.get("/self-assessment/questions").json()
    assert quiz["role"] == role and len(quiz["interview"]) == 6


def test_new_roles_get_role_specific_tasks(client):
    client.post("/update-profile", json={"target_role": "cybersecurity", "available_hours": 40})
    titles = [t["title"] for t in client.post("/generate-plan").json()["tasks"]]
    assert any("CTF" in t for t in titles)
    assert any("OWASP" in t or "incident" in t for t in titles)


def test_simulator_lists_all_roles_and_flags_the_current_one(client):
    client.post("/generate-plan")
    sims = client.get("/simulate-roles").json()
    assert [s["role"] for s in sims] == ROLES
    assert [s["role"] for s in sims if s["is_current"]] == ["swe_backend"]
    for s in sims:
        assert sum(s["hours"].values()) == 10 and set(s["hours"]) == AGENTS
        assert abs(sum(s["shares"].values()) - 100) < 0.5
        assert 0 <= s["health"] <= 100
    assert len({tuple(s["hours"].values()) for s in sims}) > 1      # roles really differ


def test_simulator_current_role_matches_the_live_allocation(client):
    live = {a["agent"]: a["hours"] for a in client.get("/allocate").json()["allocations"]}
    current = next(s for s in client.get("/simulate-roles").json() if s["is_current"])
    assert current["hours"] == live


def test_simulator_never_changes_stored_state(client):
    client.post("/generate-plan")
    before = state(client)
    client.get("/simulate-roles")
    assert state(client) == before