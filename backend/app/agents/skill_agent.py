from app.state.schemas import StateVector
from app.agents.schemas import Bid


def get_bid(state: StateVector) -> Bid:
    need = (100 - state.resume_score) / 100
    streak_bonus = 0.1 if state.streak_count >= 2 else 0.0
    bid_score = min(1.0, round(need + streak_bonus, 2))

    requested_hours = round(bid_score * state.available_hours * 0.6)

    reasons = []
    if state.resume_score < 70:
        reasons.append("resume score is below target")
    if state.streak_count >= 2:
        reasons.append(f"{state.streak_count}-week streak, momentum worth continuing")
    reasons.append(f"next skill to learn is '{state.skill_progress.next_skill}'")

    return Bid(
        agent="skill_building",
        bid_score=bid_score,
        requested_hours=requested_hours,
        reason=", ".join(reasons),
    )