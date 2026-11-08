"""Phase 8 tests: non-technical roles and the portfolio-evidence model."""
import pytest

import app.analysis.portfolio_scanner as portfolio_scanner
from app.analysis.portfolio_evidence import EvidenceError, score_portfolio_evidence
from app.roles import ROLE_LABELS, portfolio_mode, role_options

NONTECH = ["ux_designer", "business_analyst", "digital_marketer", "finance_analyst"]
TECH = ["swe_backend", "data_analyst", "frontend_dev", "ml_engineer", "cloud_devops", "cybersecurity"]
STRONG = {
    "links": ["behance.net/me/one", "https://www.dribbble.com/me", "figma.com/@me"],
    "case_studies": 4, "has_results": True, "has_process": True, "recent_work": True,
}


def state(c):
    return c.get("/state").json()


def set_role(c, role, hours=12):
    assert c.post("/update-profile", json={"target_role": role, "available_hours": hours}).status_code == 200


def portfolio_bid(c):
    return next(b["bid_score"] for b in c.get("/bids").json() if b["agent"] == "portfolio")


def test_every_role_has_a_portfolio_mode():
    assert set(ROLE_LABELS) == set(NONTECH) | set(TECH)
    assert all(portfolio_mode(r) == "evidence" for r in NONTECH)
    assert all(portfolio_mode(r) == "github" for r in TECH)
    assert {o["value"]: o["portfolio_mode"] for o in role_options()}["ux_designer"] == "evidence"


def test_roles_endpoint_reports_the_portfolio_mode(client):
    modes = {r["value"]: r["portfolio_mode"] for r in client.get("/roles").json()}
    assert modes["ux_designer"] == "evidence" and modes["swe_backend"] == "github"


def test_strong_evidence_scores_100_and_empty_scores_0():
    strong = score_portfolio_evidence(**STRONG)
    assert strong["score"] == 100 and strong["notes"] == ["Portfolio evidence looks strong"]
    empty = score_portfolio_evidence([], 0, False, False, False)
    assert empty["score"] == 0 and len(empty["notes"]) == 5


def test_each_piece_of_evidence_adds_points():
    base = score_portfolio_evidence([], 0, False, False, False)["score"]
    assert score_portfolio_evidence(["behance.net/me"], 0, False, False, False)["score"] > base
    assert score_portfolio_evidence([], 2, False, False, False)["score"] == 20
    assert score_portfolio_evidence([], 0, True, False, False)["score"] == 15
    assert score_portfolio_evidence([], 0, False, True, False)["score"] == 10
    assert score_portfolio_evidence([], 0, False, False, True)["score"] == 10


def test_links_are_cleaned_recognised_and_deduplicated():
    result = score_portfolio_evidence(
        ["www.Behance.net/me/", "https://behance.net/me", "https://janedoe.design/work"], 0, False, False, False)
    assert [l["url"] for l in result["links"]] == ["https://behance.net/me", "https://janedoe.design/work"]
    assert [l["platform"] for l in result["links"]] == ["Behance", "Personal site"]
    assert [l["recognized"] for l in result["links"]] == [True, False]


@pytest.mark.parametrize("links,cases", [
    (["not a link"], 0), (["ftp://example.com"], 0), (["nodot"], 0),
    (["a.com/" + "x" * 300], 0), (["a.com", "b.com", "c.com", "d.com", "e.com", "f.com"], 0),
    ([], -1), ([], 21),
])
def test_invalid_evidence_is_rejected(links, cases):
    with pytest.raises(EvidenceError):
        score_portfolio_evidence(links, cases, False, False, False)


def test_evidence_endpoint_updates_the_portfolio(client):
    set_role(client, "ux_designer")
    r = client.post("/portfolio-evidence", json=STRONG)
    assert r.status_code == 200 and r.json()["score"] == 100
    s = state(client)
    assert s["portfolio_score"] == 100 and s["portfolio_details"]["mode"] == "evidence"
    assert len(s["portfolio_details"]["links"]) == 3 and s["portfolio_notes"] == "Portfolio evidence looks strong"


def test_stronger_evidence_lowers_the_portfolio_bid(client):
    set_role(client, "digital_marketer")
    client.post("/portfolio-evidence", json={})
    weak = portfolio_bid(client)
    client.post("/portfolio-evidence", json=STRONG)
    assert portfolio_bid(client) < weak


def test_weak_evidence_shows_up_in_the_explanation(client):
    set_role(client, "finance_analyst")
    client.post("/portfolio-evidence", json={"case_studies": 1})
    body = client.get("/dashboard").json()
    d = body[0] if isinstance(body, list) else body
    text = next(i["explanation"] for i in d["explanations"]["items"] if i["agent"] == "portfolio")
    assert "Add at least 3 portfolio links" in text


def test_each_route_only_accepts_its_own_kind_of_portfolio(client, monkeypatch):
    assert client.post("/portfolio-evidence", json=STRONG).status_code == 422       # backend role
    set_role(client, "ux_designer")
    before = state(client)
    r = client.post("/analyze-portfolio", json={"github_username": "someone"})
    assert r.status_code == 422 and "portfolio evidence" in r.json()["detail"]
    assert state(client) == before


def test_invalid_evidence_changes_nothing(client):
    set_role(client, "ux_designer")
    before = state(client)
    assert client.post("/portfolio-evidence", json={"links": ["not a link"]}).status_code == 422
    assert client.post("/portfolio-evidence", json={"case_studies": 99}).status_code == 422
    assert state(client) == before


def test_switching_portfolio_kind_resets_the_old_score(client, monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return [{"fork": False, "description": "d"} for _ in range(5)]

    monkeypatch.setattr(portfolio_scanner.requests, "get", lambda *a, **k: FakeResponse())
    client.post("/analyze-portfolio", json={"github_username": "someone"})
    assert state(client)["portfolio_score"] == 100
    set_role(client, "ux_designer")
    s = state(client)
    assert s["portfolio_score"] == 50 and s["portfolio_details"] == {} and s["portfolio_notes"] == ""


def test_staying_in_the_same_portfolio_kind_keeps_the_evidence(client):
    set_role(client, "ux_designer")
    client.post("/portfolio-evidence", json=STRONG)
    set_role(client, "business_analyst")
    s = state(client)
    assert s["portfolio_score"] == 100 and s["portfolio_details"]["mode"] == "evidence"
    set_role(client, "data_analyst")                       # evidence -> github resets it
    assert state(client)["portfolio_score"] == 50


@pytest.mark.parametrize("role", NONTECH)
def test_non_technical_plans_do_not_mention_github_or_dsa(client, role):
    set_role(client, role, hours=60)
    titles = [t["title"] for t in client.post("/generate-plan").json()["tasks"]]
    assert titles and all("GitHub" not in t and "DSA" not in t and "commit" not in t for t in titles)
    assert any("case study" in t.lower() or "campaign" in t.lower() or "analysis" in t.lower()
               or "model" in t.lower() or "process" in t.lower() for t in titles)