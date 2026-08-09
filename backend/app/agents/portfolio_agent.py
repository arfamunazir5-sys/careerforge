from app.state.schemas import StateVector
from app.agents.schemas import Bid


def get_bid(state: StateVector) -> Bid:
    need = (100 - state.portfolio_score) / 100
    bid_score = round(need, 2)
    requested_hours = round(bid_score * state.available_hours * 0.3)

    reason = (
        "portfolio score is below target"
        if state.portfolio_score < 60
        else "portfolio is in reasonable shape"
    )

    return Bid(
        agent="portfolio",
        bid_score=bid_score,
        requested_hours=requested_hours,
        reason=reason,
    )