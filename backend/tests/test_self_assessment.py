"""Phase 3 tests: question banks, scoring, validation, and how the assessment
feeds the agents without showing up as fake task progress."""
import pytest

from app.agents.role_weights import ROLE_WEIGHTS
from app.analysis.self_assessment import INTERVIEW_BANK, NETWORKING_QUESTIONS


def state(c):
    return c.get("/state").json()


def dashboard(c):
    body = c.get("/dashboard").json()
    return body[0] if isinstance(body, list) else body


def interview_bid(c):
    return next(b["bid_score"] for b in c.get("/bids").json() if b["agent"] == "interview_prep")


def all_correct():
    role_bank = INTERVIEW_BANK["swe_backend"]
    return {q["id"]: q["answer"] for q in role_bank}


def all_wrong():
    return {q["id"]: (q["answer"] + 1) % len(q["options"]) for q in INTERVIEW_BANK["swe_backend"]}


def networking(points):
    return {q["id"]: points for q in NETWORKING_QUESTIONS}


def test_question_banks_are_well_formed():
    ids = []
    for role in ROLE_WEIGHTS:
        bank = INTERVIEW_BANK[role]
        assert len(bank) >= 6
        for q in bank:
            ids.append(q["id"])
            assert len(q["options"]) == 4 and 0 <= q["answer"] < 4 and q["topic"] and q["prompt"]
        assert len({q["answer"] for q in bank}) > 1      # the right answer is not always the same slot
    assert len(ids) == len(set(ids))
    assert len(NETWORKING_QUESTIONS) == 4
    assert all(len(q["options"]) == 4 for q in NETWORKING_QUESTIONS)


def test_questions_endpoint_hides_answers_and_uses_state_role(client):
    data = client.get("/self-assessment/questions").json()
    assert data["role"] == "swe_backend"
    assert len(data["interview"]) == len(INTERVIEW_BANK["swe_backend"])
    for q in data["interview"]:
        assert set(q) == {"id", "prompt", "options"}
    client.post("/update-profile", json={"target_role": "data_analyst", "available_hours": 10})
    assert client.get("/self-assessment/questions").json()["interview"][0]["id"].startswith("da-")


def test_perfect_interview_answers(client):
    r = client.post("/self-assessment", json={"interview_answers": all_correct()})
    assert r.status_code == 200
    body = r.json()["interview"]
    assert body["score"] == 100 and body["correct"] == body["total"] and body["missed_topics"] == []
    s = state(client)
    assert s["interview_score"] == 100
    assert s["assessment"]["interview"]["score"] == 100


def test_all_wrong_interview_answers_list_topics_to_review(client):
    body = client.post("/self-assessment", json={"interview_answers": all_wrong()}).json()["interview"]
    assert body["score"] == 0 and len(body["missed_topics"]) == body["total"]
    assert state(client)["interview_score"] == 0


def test_interview_score_moves_the_interview_bid_the_right_way(client):
    base = interview_bid(client)
    client.post("/self-assessment", json={"interview_answers": all_correct()})
    strong = interview_bid(client)
    client.post("/self-assessment", json={"interview_answers": all_wrong()})
    weak = interview_bid(client)
    assert strong < base < weak


def test_networking_best_and_worst_answers(client):
    assert client.post("/self-assessment", json={"networking_answers": networking(3)}).json()["networking"]["score"] == 100
    assert state(client)["networking_score"] == 100
    assert client.post("/self-assessment", json={"networking_answers": networking(0)}).json()["networking"]["score"] == 0
    assert state(client)["networking_score"] == 0


def test_confidence_only_changes_confidence(client):
    before = state(client)
    r = client.post("/self-assessment", json={"confidence": 9})
    assert r.json()["confidence"] == 9
    after = state(client)
    assert after["confidence"] == 9 and after["assessment"]["confidence"] == 9
    assert after["interview_score"] == before["interview_score"]
    assert after["networking_score"] == before["networking_score"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"interview_answers": {"be-1": 1}},                                   # partial
        {"interview_answers": {**all_correct(), "zz-9": 0}},                  # unknown question
        {"interview_answers": {**all_correct(), "be-1": 7}},                  # option out of range
        {"interview_answers": {**all_correct(), "be-1": -1}},
        {"networking_answers": {"net-1": 1}},                                 # partial
        {"networking_answers": {**networking(1), "net-2": 4}},
        {"confidence": 0},
        {"confidence": 11},
    ],
)
def test_invalid_assessments_are_rejected_and_change_nothing(client, payload):
    before = state(client)
    assert client.post("/self-assessment", json=payload).status_code == 422
    assert state(client) == before


def test_assessment_is_not_reported_as_task_progress(client):
    client.post("/generate-plan")
    client.post("/self-assessment", json={"interview_answers": all_correct(), "networking_answers": networking(3)})
    s = state(client)
    assert s["plan_snapshot"]["scores"]["Interview"] == 100
    assert s["plan_snapshot"]["scores"]["Networking"] == 100
    assert dashboard(client)["adaptation"]["progress"] == []


def test_role_change_clears_quiz_result_but_keeps_networking(client):
    client.post("/self-assessment", json={
        "interview_answers": all_correct(), "networking_answers": networking(2), "confidence": 8})
    client.post("/update-profile", json={"target_role": "data_analyst", "available_hours": 10})
    a = state(client)["assessment"]
    assert "interview" not in a
    assert a["networking"]["score"] == 67 and a["confidence"] == 8


def test_reset_clears_assessment(client):
    client.post("/self-assessment", json={"confidence": 8})
    client.post("/reset")
    assert state(client)["assessment"] == {}