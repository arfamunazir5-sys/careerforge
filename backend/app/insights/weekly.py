from typing import Optional, Tuple
from app.state.schemas import StateVector
from app.plan.schemas import WeeklyPlan
from app.insights.adaptation import current_scores

HISTORY_LIMIT = 12


def summarize_week(state: StateVector, plan: WeeklyPlan) -> dict:
    """What happened this week, read from the stored plan and the score snapshot
    taken when the plan was built."""
    tasks = plan.tasks
    done = [t for t in tasks if t.status == "done"]
    ignored = [t for t in tasks if t.status == "ignored"]
    pending = [t for t in tasks if t.status == "pending"]
    hours_total = sum(t.hours for t in tasks)
    hours_done = sum(t.hours for t in done)

    now = current_scores(state)
    before = (state.plan_snapshot or {}).get("scores", {})
    score_changes = {
        module: now[module] - before[module]
        for module in now
        if module in before and now[module] != before[module]
    }

    return {
        "week_number": state.week_number,
        "tasks_total": len(tasks),
        "done": len(done),
        "ignored": len(ignored),
        "pending": len(pending),
        "hours_total": hours_total,
        "hours_done": hours_done,
        "completion_pct": round(len(done) / len(tasks) * 100) if tasks else 0,
        "score_changes": score_changes,
    }


def close_week(
    state: StateVector,
    plan: WeeklyPlan,
    available_hours: Optional[int] = None,
    confidence: Optional[int] = None,
) -> Tuple[dict, dict]:
    """Returns (state updates, summary) for closing the current week. Pure: it
    does not write anything."""
    summary = summarize_week(state, plan)
    history = list(state.week_history or [])
    history.append({**summary, "role": state.target_role})
    history = history[-HISTORY_LIMIT:]

    updates = {
        "week_number": state.week_number + 1,
        "completed_tasks_last_week": summary["done"],
        "ignored_tasks_last_week": summary["ignored"],
        "week_history": history,
    }
    if available_hours is not None:
        updates["available_hours"] = available_hours
    if confidence is not None:
        updates["confidence"] = confidence
    return updates, summary