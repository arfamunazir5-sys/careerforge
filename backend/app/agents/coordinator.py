from typing import List
from app.state.schemas import StateVector
from app.agents.schemas import Bid, Allocation, AgentAllocation
from app.agents.role_weights import get_weights_for_role


def allocate(state: StateVector, bids: List[Bid]) -> Allocation:
    role_weights = get_weights_for_role(state.target_role)

    # combine each agent's bid strength with how important that
    # domain is for this specific target role
    combined_scores = {}
    for bid in bids:
        role_weight = role_weights.get(bid.agent, 0.25)
        combined_scores[bid.agent] = bid.bid_score * role_weight

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