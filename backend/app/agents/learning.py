"""Learning from follow-through: a small, bounded, explainable weight per agent.

Every time the user completes or ignores a task, that outcome is recorded for the
task's agent (last WINDOW outcomes). The follow-through rate is a smoothed estimate
(a Beta(1, 1) prior), so one outcome never swings the plan. The rate becomes a weight
multiplier on the agent's bid: agents whose tasks keep being ignored get less time,
never less than 1 - MAX_PENALTY, so no agent is ever starved. By default, completing
tasks does not boost an agent (MAX_BOOST = 0): need still decides priorities, and
follow-through only trims what the user is not doing."""

AGENTS = ["skill_building", "networking", "portfolio", "interview_prep"]
WINDOW = 20
MAX_PENALTY = 0.3
MAX_BOOST = 0.0


def follow_through(outcomes: list) -> float:
    """Smoothed share of recent tasks that were completed (0 to 1)."""
    if not outcomes:
        return 0.5
    return (sum(outcomes) + 1) / (len(outcomes) + 2)


def multiplier_for(outcomes: list, max_penalty: float = MAX_PENALTY, max_boost: float = MAX_BOOST) -> float:
    delta = 2 * follow_through(outcomes) - 1  # -1 (all ignored) .. +1 (all completed)
    scale = max_boost if delta > 0 else max_penalty
    return round(1 + scale * delta, 4)


def record_outcome(outcomes_by_agent: dict, agent: str, success: bool) -> dict:
    """Returns a new outcomes dict with this outcome added (oldest dropped past WINDOW)."""
    updated = {a: list(v) for a, v in (outcomes_by_agent or {}).items()}
    history = updated.get(agent, [])
    history.append(1 if success else 0)
    updated[agent] = history[-WINDOW:]
    return updated


def agent_multipliers(state) -> dict:
    outcomes = getattr(state, "agent_outcomes", None) or {}
    return {agent: multiplier_for(outcomes.get(agent, [])) for agent in AGENTS}


def summarize_learning(state) -> dict:
    outcomes = getattr(state, "agent_outcomes", None) or {}
    summary = {}
    for agent in AGENTS:
        history = outcomes.get(agent, [])
        summary[agent] = {
            "multiplier": multiplier_for(history),
            "followed": sum(history),
            "total": len(history),
            "rate": round(follow_through(history), 2),
        }
    return summary