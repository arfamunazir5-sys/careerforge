from app.state.schemas import StateVector, SkillProgress
from app.analysis.skill_graph import get_next_skill
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate, compute_shares
from app.insights.career_health import compute_career_health
from app.roles import ROLE_LABELS


def simulate_all_roles(state: StateVector) -> list:
    """Read-only: how the plan and health score would look for each role, using
    the user's current scores and hours. Never writes any state."""
    results = []
    for role, label in ROLE_LABELS.items():
        completed = list(state.skill_progress.completed_skills)
        sim = state.model_copy(
            update={
                "target_role": role,
                "skill_progress": SkillProgress(
                    completed_skills=completed,
                    next_skill=get_next_skill(role, completed),
                ),
                "skill_task_progress": state.skill_task_progress if role == state.target_role else 0,
            }
        )
        bids = [
            skill_agent.get_bid(sim),
            networking_agent.get_bid(sim),
            portfolio_agent.get_bid(sim),
            interview_agent.get_bid(sim),
        ]
        allocation = allocate(sim, bids)
        results.append(
            {
                "role": role,
                "label": label,
                "is_current": role == state.target_role,
                "hours": {a.agent: a.hours for a in allocation.allocations},
                "shares": compute_shares(sim, bids),
                "health": compute_career_health(sim).overall_score,
                "next_skill": sim.skill_progress.next_skill,
            }
        )
    return results