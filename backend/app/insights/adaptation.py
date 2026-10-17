from app.state.schemas import StateVector
from app.agents.schemas import Allocation

AGENT_TO_MODULE = {
    "skill_building": "Resume",
    "portfolio": "Portfolio",
    "networking": "Networking",
    "interview_prep": "Interview",
}

AGENT_LABELS = {
    "skill_building": "Skill Building",
    "portfolio": "Portfolio",
    "networking": "Networking",
    "interview_prep": "Interview Prep",
}


def current_scores(state: StateVector) -> dict:
    return {
        "Resume": state.resume_score,
        "Portfolio": state.portfolio_score,
        "Networking": state.networking_score,
        "Interview": state.interview_score,
    }


def build_snapshot(state: StateVector, allocation: Allocation) -> dict:
    return {
        "scores": current_scores(state),
        "allocation": {a.agent: a.hours for a in allocation.allocations},
        "role": state.target_role,
        "hours": state.available_hours,
    }


def _state_key(snapshot: dict):
    return (snapshot.get("scores"), snapshot.get("role"), snapshot.get("hours"))


def snapshot_update(state: StateVector, allocation: Allocation) -> dict:
    """Fields to store when a new plan is generated. The old snapshot only
    moves into previous_plan_snapshot when something genuinely changed since
    it was taken, so regenerating with no progress can't erase a real
    comparison."""
    new_snapshot = build_snapshot(state, allocation)
    old_snapshot = state.plan_snapshot or {}

    if old_snapshot and _state_key(old_snapshot) != _state_key(new_snapshot):
        return {"previous_plan_snapshot": old_snapshot, "plan_snapshot": new_snapshot}
    return {"plan_snapshot": new_snapshot}


def compute_adaptation(state: StateVector) -> dict:
    live = current_scores(state)
    snap = state.plan_snapshot or {}
    prev = state.previous_plan_snapshot or {}

    # 1) Live progress since the current plan was generated
    progress = []
    snap_scores = snap.get("scores", {})
    for module, after in live.items():
        before = snap_scores.get(module)
        if before is not None and before != after:
            progress.append(
                {"module": module, "before": before, "after": after, "change": after - before}
            )

    # 2) How hours shifted between the previous plan and the current one.
    # Only comparable when role and hour budget match.
    reallocation = []
    comparable = (
        bool(prev)
        and bool(snap)
        and prev.get("role") == snap.get("role")
        and prev.get("hours") == snap.get("hours")
    )
    if comparable:
        for agent, hours_now in snap.get("allocation", {}).items():
            hours_before = prev.get("allocation", {}).get(agent)
            if hours_before is None or hours_before == hours_now:
                continue

            module = AGENT_TO_MODULE.get(agent)
            score_before = prev.get("scores", {}).get(module)
            score_after = snap.get("scores", {}).get(module)

            # A causal sentence is only written for the case the bid formula
            # actually supports: score went up, so need went down, so hours fell.
            note = ""
            if (
                score_before is not None
                and score_after is not None
                and score_after > score_before
                and hours_now < hours_before
            ):
                note = (
                    f"{AGENT_LABELS.get(agent, agent)} improved "
                    f"({score_before} → {score_after}), so it needed less time."
                )

            reallocation.append(
                {"agent": agent, "before": hours_before, "after": hours_now, "note": note}
            )

    return {"progress": progress, "reallocation": reallocation}