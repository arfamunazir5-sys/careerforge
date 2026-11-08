from typing import List
from app.state.schemas import StateVector
from app.agents.schemas import Bid, Allocation, AgentAllocation
from app.agents.role_weights import get_weights_for_role
from app.agents.learning import agent_multipliers


def allocate(state: StateVector, bids: List[Bid]) -> Allocation:
    role_weights = get_weights_for_role(state.target_role)
    multipliers = agent_multipliers(state)

    # combine each agent's bid strength with how important that domain is for
    # this specific target role, and how well the user follows through on its tasks
    combined_scores = {}
    for bid in bids:
        role_weight = role_weights.get(bid.agent, 0.25)
        combined_scores[bid.agent] = bid.bid_score * role_weight * multipliers.get(bid.agent, 1.0)

    total_score = sum(combined_scores.values())

    if total_score == 0:
        # fallback: nobody scored anything, split hours evenly
        equal_share = state.available_hours // len(bids)
        allocations = [
            AgentAllocation(agent=bid.agent, hours=equal_share) for bid in bids
        ]
        return Allocation(week_number=state.week_number, allocations=allocations)

    # normalize combined scores so they sum to 1, then convert to hours
    raw_hours = {
        agent: (score / total_score) * state.available_hours
        for agent, score in combined_scores.items()
    }

    # round down first, then hand out leftover hours to whoever has
    # the biggest fractional remainder, so total always equals available_hours
    rounded_hours = {agent: int(hours) for agent, hours in raw_hours.items()}
    leftover = state.available_hours - sum(rounded_hours.values())

    remainders = sorted(
        raw_hours.items(), key=lambda item: item[1] - int(item[1]), reverse=True
    )
    for i in range(leftover):
        agent = remainders[i % len(remainders)][0]
        rounded_hours[agent] += 1

    allocations = [
        AgentAllocation(agent=agent, hours=hours)
        for agent, hours in rounded_hours.items()
    ]

    return Allocation(week_number=state.week_number, allocations=allocations)


def compute_shares(state: StateVector, bids: List[Bid]) -> dict:
    """Each agent's unrounded share of the week, in percent (one decimal).
    Same math as allocate(), before whole-hour rounding, so small changes in
    scores are visible even when the whole-hour split does not move."""
    role_weights = get_weights_for_role(state.target_role)
    multipliers = agent_multipliers(state)
    combined = {
        b.agent: b.bid_score * role_weights.get(b.agent, 0.25) * multipliers.get(b.agent, 1.0)
        for b in bids
    }
    total = sum(combined.values())
    if total == 0:
        return {b.agent: round(100 / len(bids), 1) for b in bids}
    return {agent: round(score / total * 100, 1) for agent, score in combined.items()}