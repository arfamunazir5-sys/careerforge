from app.state.state_builder import get_current_state
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate
from app.insights.adaptation import snapshot_update, compute_adaptation


def _allocation_for(state):
    bids = [
        skill_agent.get_bid(state),
        networking_agent.get_bid(state),
        portfolio_agent.get_bid(state),
        interview_agent.get_bid(state),
    ]
    return allocate(state, bids)


def _clean_state():
    return get_current_state().model_copy(
        update={"plan_snapshot": {}, "previous_plan_snapshot": {}}
    )


def test_no_snapshot_means_nothing_to_show():
    result = compute_adaptation(_clean_state())
    assert result == {"progress": [], "reallocation": []}


def test_first_plan_stores_snapshot_without_previous():
    state = _clean_state()
    update = snapshot_update(state, _allocation_for(state))
    assert "plan_snapshot" in update
    assert "previous_plan_snapshot" not in update


def test_progress_only_appears_when_scores_actually_changed():
    base = _clean_state()
    snapshot = snapshot_update(base, _allocation_for(base))["plan_snapshot"]

    unchanged = base.model_copy(update={"plan_snapshot": snapshot})
    assert compute_adaptation(unchanged)["progress"] == []

    improved = unchanged.model_copy(update={"networking_score": base.networking_score + 3})
    progress = compute_adaptation(improved)["progress"]
    assert len(progress) == 1
    assert progress[0]["module"] == "Networking"
    assert progress[0]["change"] == 3


def test_regenerating_without_changes_keeps_previous_snapshot():
    base = _clean_state()
    first = snapshot_update(base, _allocation_for(base))["plan_snapshot"]

    improved = base.model_copy(
        update={"plan_snapshot": first, "networking_score": base.networking_score + 20}
    )
    rotated = snapshot_update(improved, _allocation_for(improved))
    assert rotated["previous_plan_snapshot"] == first

    after = improved.model_copy(update=rotated)
    again = snapshot_update(after, _allocation_for(after))
    assert "previous_plan_snapshot" not in again


def test_reallocation_only_when_budget_and_role_match():
    state = get_current_state()
    prev = {
        "scores": {"Resume": 60, "Portfolio": 50, "Networking": 40, "Interview": 55},
        "allocation": {"skill_building": 4, "networking": 2, "portfolio": 2, "interview_prep": 2},
        "role": state.target_role,
        "hours": state.available_hours,
    }
    snap = {
        "scores": {"Resume": 60, "Portfolio": 50, "Networking": 55, "Interview": 55},
        "allocation": {"skill_building": 5, "networking": 1, "portfolio": 2, "interview_prep": 2},
        "role": state.target_role,
        "hours": state.available_hours,
    }

    result = compute_adaptation(
        state.model_copy(update={"plan_snapshot": snap, "previous_plan_snapshot": prev})
    )
    by_agent = {r["agent"]: r for r in result["reallocation"]}
    assert by_agent["networking"]["before"] == 2 and by_agent["networking"]["after"] == 1
    assert "improved" in by_agent["networking"]["note"]
    assert by_agent["skill_building"]["note"] == ""
    assert "portfolio" not in by_agent

    other_budget = {**snap, "hours": state.available_hours + 5}
    result2 = compute_adaptation(
        state.model_copy(update={"plan_snapshot": other_budget, "previous_plan_snapshot": prev})
    )
    assert result2["reallocation"] == []