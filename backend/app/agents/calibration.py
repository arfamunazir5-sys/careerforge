"""Single home for the tuning constants and curves that decide how strongly
each agent's bid reacts to progress. Change numbers here, not in the agents."""
from typing import List, Tuple

from app.analysis.skill_graph import get_full_chain

# Score at which a domain counts as "good enough". Need is measured against it.
TARGET_SCORE = 70
# Need never hits zero, so no agent drops out of the plan completely.
MIN_NEED = 0.05

# Skill agent: how much each signal contributes to its bid.
SKILL_ROADMAP_WEIGHT = 0.30
SKILL_RESUME_WEIGHT = 0.10

# Momentum from a streak. Ending the streak removes it.
MOMENTUM_PER_STREAK = 0.025
MAX_MOMENTUM = 0.10

# Mirrors TASKS_PER_SKILL in app/tracker/progress_tracker.py.
TASKS_PER_SKILL = 3


def need_from_score(score: float) -> float:
    """0..1 need for a domain. Falls linearly to MIN_NEED as score nears TARGET_SCORE."""
    need = (TARGET_SCORE - score) / TARGET_SCORE
    return max(MIN_NEED, min(1.0, need))


def momentum_bonus(streak_count: int) -> float:
    """Smooth streak bonus, capped. A streak of 0 gives nothing."""
    return min(MAX_MOMENTUM, MOMENTUM_PER_STREAK * max(0, streak_count))


def roadmap_progress(
    target_role: str, completed_skills: List[str], skill_task_progress: int
) -> Tuple[float, int, int]:
    """Returns (fraction_done, skills_done, total_skills) for the role's roadmap.
    Counts only completed skills that are actually in this role's chain, plus
    partial credit for tasks finished toward the current skill."""
    chain = get_full_chain(target_role)
    if not chain:
        return 0.0, 0, 0
    done = sum(1 for skill in chain if skill in completed_skills)
    partial = max(0, min(skill_task_progress, TASKS_PER_SKILL - 1)) / TASKS_PER_SKILL
    fraction = min(1.0, (done + partial) / len(chain))
    return fraction, done, len(chain)