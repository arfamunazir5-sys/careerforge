from app.state.state_builder import get_current_state
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate
from app.plan.plan_generator import generate_plan


def test_plan_generator_matches_allocation_hours():
    state = get_current_state()
    bids = [
        skill_agent.get_bid(state),
        networking_agent.get_bid(state),
        portfolio_agent.get_bid(state),
        interview_agent.get_bid(state),
    ]
    allocation = allocate(state, bids)
    plan = generate_plan(state, allocation)

    assert plan.week_number == state.week_number
    assert len(plan.tasks) > 0

    total_task_hours = sum(t.hours for t in plan.tasks)
    total_allocated_hours = sum(a.hours for a in allocation.allocations)
    assert total_task_hours == total_allocated_hours

    for t in plan.tasks:
        assert t.status == "pending"
        print(f"{t.id} [{t.agent}] {t.hours}h: {t.title}")
        