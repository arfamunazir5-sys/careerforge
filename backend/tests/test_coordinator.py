from app.state.state_builder import get_current_state
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate


def test_allocation_uses_full_budget_and_valid_shape():
    state = get_current_state()
    bids = [
        skill_agent.get_bid(state),
        networking_agent.get_bid(state),
        portfolio_agent.get_bid(state),
        interview_agent.get_bid(state),
    ]

    result = allocate(state, bids)

    assert result.week_number == state.week_number
    assert len(result.allocations) == 4

    total_allocated = sum(a.hours for a in result.allocations)
    assert total_allocated == state.available_hours

    for a in result.allocations:
        assert a.hours >= 0
        print(f"{a.agent}: {a.hours}h")