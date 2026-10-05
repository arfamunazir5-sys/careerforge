from typing import List
from app.state.schemas import StateVector
from app.agents.schemas import Bid, Allocation
from app.agents.role_weights import get_weights_for_role
from app.insights.schemas import ExplainabilityResult, ExplanationItem

AGENT_LABELS = {
    "skill_building": "Skill Building",
    "networking": "Networking",
    "portfolio": "Portfolio",
    "interview_prep": "Interview Prep",
}

ROLE_LABELS = {
    "swe_backend": "Backend Developer",
    "data_analyst": "Data Analyst",
    "frontend_dev": "Frontend Developer",
}

# Only Resume and Portfolio currently have persisted analysis notes (Step 2/3) —
# Networking and Interview have no analyzer, so no note field to reference.
NOTE_FIELD_MAP = {
    "skill_building": "resume_notes",
    "portfolio": "portfolio_notes",
}


def generate_explanations(state: StateVector, bids: List[Bid], allocation: Allocation) -> ExplainabilityResult:
    bid_by_agent = {b.agent: b for b in bids}
    role_weights = get_weights_for_role(state.target_role)
    role_label = ROLE_LABELS.get(state.target_role, state.target_role.replace("_", " ").title())
    items = []

    for agent_allocation in allocation.allocations:
        agent = agent_allocation.agent
        hours = agent_allocation.hours
        bid = bid_by_agent.get(agent)

        label = AGENT_LABELS.get(agent, agent)
        parts = [f"{label} received {hours}h this week."]

        weight = role_weights.get(agent)
        if weight:
            parts.append(f"Your {role_label} goal weights this area at {int(weight * 100)}% priority.")

        if bid:
            parts.append(bid.reason.capitalize() + ".")

        note_field = NOTE_FIELD_MAP.get(agent)
        if note_field:
            note = getattr(state, note_field, "")
            if note:
                parts.append(note + ".")

        if bid:
            if hours < bid.requested_hours:
                parts.append(
                    f"It requested {bid.requested_hours}h but other agents had a stronger case this week."
                )
            elif bid.requested_hours > 0 and hours >= bid.requested_hours:
                parts.append("It received its full requested share.")

        items.append(ExplanationItem(agent=agent, hours=hours, explanation=" ".join(parts)))

    return ExplainabilityResult(week_number=state.week_number, items=items)