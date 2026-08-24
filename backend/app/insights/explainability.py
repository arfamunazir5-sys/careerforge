from typing import List
from app.state.schemas import StateVector
from app.agents.schemas import Bid, Allocation
from app.insights.schemas import ExplainabilityResult, ExplanationItem

AGENT_LABELS = {
    "skill_building": "Skill Building",
    "networking": "Networking",
    "portfolio": "Portfolio",
    "interview_prep": "Interview Prep",
}


def generate_explanations(state: StateVector, bids: List[Bid], allocation: Allocation) -> ExplainabilityResult:
    bid_by_agent = {b.agent: b for b in bids}
    items = []

    for agent_allocation in allocation.allocations:
        agent = agent_allocation.agent
        hours = agent_allocation.hours
        bid = bid_by_agent.get(agent)

        label = AGENT_LABELS.get(agent, agent)
        parts = [f"{label} received {hours}h this week."]

        if bid:
            parts.append(bid.reason.capitalize() + ".")
            if hours < bid.requested_hours:
                parts.append(
                    f"It requested {bid.requested_hours}h but other agents had a stronger case this week."
                )
            elif bid.requested_hours > 0 and hours >= bid.requested_hours:
                parts.append("It received its full requested share.")

        items.append(ExplanationItem(agent=agent, hours=hours, explanation=" ".join(parts)))

    return ExplainabilityResult(week_number=state.week_number, items=items)