from app.state.schemas import StateVector
from app.agents.schemas import Bid
from app.agents.calibration import (
    SKILL_ROADMAP_WEIGHT,
    SKILL_RESUME_WEIGHT,
    need_from_score,
    momentum_bonus,
    roadmap_progress,
)


def get_bid(state: StateVector) -> Bid:
    fraction_done, skills_done, skills_total = roadmap_progress(
        state.target_role,
        state.skill_progress.completed_skills,
        state.skill_task_progress,
    )
    roadmap_remaining = 1.0 - fraction_done
    resume_need = need_from_score(state.resume_score)
    momentum = momentum_bonus(state.streak_count)

    bid_score = min(
        1.0,
        round(
            SKILL_ROADMAP_WEIGHT * roadmap_remaining
            + SKILL_RESUME_WEIGHT * resume_need
            + momentum,
            2,
        ),
    )

    requested_hours = round(bid_score * state.available_hours * 0.6)

    reasons = []
    if skills_total:
        reasons.append(f"{skills_done}/{skills_total} roadmap skills done")
    if state.resume_score < 70:
        reasons.append("resume score is below target")
    if state.streak_count >= 2:
        reasons.append(f"{state.streak_count}-week streak, momentum worth continuing")
    reasons.append(f"next skill to learn is '{state.skill_progress.next_skill}'")

    return Bid(
        agent="skill_building",
        bid_score=bid_score,
        requested_hours=requested_hours,
        reason=", ".join(reasons),
    )