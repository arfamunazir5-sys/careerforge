from app.state.schemas import StateVector
from app.agents.schemas import Bid


def get_bid(state: StateVector) -> Bid:
    need = (100 - state.networking_score) / 100
    bid_score = round(need, 2)
    requested_hours = round(bid_score * state.available_hours * 0.3)

    reason = (
        "networking score is low, needs attention"
        if state.networking_score < 50
        else "networking score is in a reasonable range"
    )

    return Bid(
        agent="networking",
        bid_score=bid_score,
        requested_hours=requested_hours,
        reason=reason,
    )