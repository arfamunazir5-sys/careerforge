def compute_reward(status: str, streak_count: int) -> int:
    """
    +5 if a task is completed
    +10 bonus if completed while already on a streak (streak_count >= 1)
    -5 if a task is ignored

    Note: '+20 if interview improves' and '-10 if weekly goal missed' are
    week-level checks (not per-task) — we're deferring those to Phase 8
    when we build the full weekly close-out logic, to keep this phase focused.
    """
    reward = 0
    if status == "done":
        reward += 5
        if streak_count >= 1:
            reward += 10
    elif status == "ignored":
        reward -= 5
    return reward