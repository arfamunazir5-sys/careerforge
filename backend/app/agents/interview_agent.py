from app.state.schemas import StateVector
from app.agents.schemas import Bid
from app.agents.calibration import need_from_score


def get_bid(state: StateVector) -> Bid:
    need = need_from_score(state.interview_score)
    confidence_gap = (10 - state.confidence) / 10
    bid_score = min(1.0, round((need + confidence_gap) / 2, 2))

    requested_hours = round(bid_score * state.available_hours * 0.3)

    reasons = []
    if state.interview_score < 70:
        reasons.append("interview score is below target")
    if state.confidence < 7:
        reasons.append("self-rated confidence is low")
    if not reasons:
        reasons.append("interview readiness is currently solid")

    return Bid(
        agent="interview_prep",
        bid_score=bid_score,
        requested_hours=requested_hours,
        reason=", ".join(reasons),
    )