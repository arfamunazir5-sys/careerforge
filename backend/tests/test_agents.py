from app.state.state_builder import get_current_state
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent


def test_all_agents_return_valid_bids():
    state = get_current_state()

    bids = [
        skill_agent.get_bid(state),
        networking_agent.get_bid(state),
        portfolio_agent.get_bid(state),
        interview_agent.get_bid(state),
    ]

    assert len(bids) == 4
    for bid in bids:
        assert 0 <= bid.bid_score <= 1
        assert bid.requested_hours >= 0
        assert bid.agent in ["skill_building", "networking", "portfolio", "interview_prep"]
        print(f"{bid.agent}: score={bid.bid_score}, hours={bid.requested_hours}, reason={bid.reason}")