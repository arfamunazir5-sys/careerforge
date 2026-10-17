"""Read-only probe: prints every agent's bid under several scenarios.
Run from the backend folder:  python scripts\\calibration_probe.py
Never writes mock_state.json."""
import sys
import pkgutil
import importlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.agents as agents_pkg
from app.state.state_builder import get_current_state
from app.analysis.skill_graph import get_next_skill


def load_bidders():
    bidders = {}
    for m in pkgutil.iter_modules(agents_pkg.__path__):
        try:
            mod = importlib.import_module(f"app.agents.{m.name}")
        except Exception as e:
            print(f"  (skipped {m.name}: {e})")
            continue
        fn = getattr(mod, "get_bid", None)
        if callable(fn):
            bidders[m.name] = fn
    return bidders


def clone(state):
    if hasattr(state, "model_copy"):
        return state.model_copy(deep=True)
    return state.copy(deep=True)


def bump(s, field, delta, cap=100):
    if hasattr(s, field):
        setattr(s, field, min(cap, getattr(s, field) + delta))


def scenario_baseline(s):
    return s


def scenario_networking_week(s):
    bump(s, "networking_score", 9)
    bump(s, "streak_count", 3, cap=999)
    bump(s, "completed_tasks_last_week", 3, cap=999)
    return s


def scenario_portfolio_week(s):
    bump(s, "portfolio_score", 9)
    bump(s, "streak_count", 3, cap=999)
    bump(s, "completed_tasks_last_week", 3, cap=999)
    return s


def scenario_interview_week(s):
    bump(s, "interview_score", 9)
    bump(s, "streak_count", 3, cap=999)
    bump(s, "completed_tasks_last_week", 3, cap=999)
    return s


def scenario_skill_completed(s):
    sp = s.skill_progress
    if sp.next_skill not in sp.completed_skills:
        sp.completed_skills.append(sp.next_skill)
    sp.next_skill = get_next_skill(s.target_role, sp.completed_skills)
    bump(s, "streak_count", 3, cap=999)
    return s


def scenario_ignored(s):
    bump(s, "ignored_tasks_last_week", 2, cap=999)
    if hasattr(s, "streak_count"):
        s.streak_count = 0
    return s


SCENARIOS = [
    ("baseline", scenario_baseline),
    ("networking week done", scenario_networking_week),
    ("portfolio week done", scenario_portfolio_week),
    ("interview week done", scenario_interview_week),
    ("skill completed", scenario_skill_completed),
    ("2 tasks ignored", scenario_ignored),
]


def collect(state, bidders):
    out = {}
    for name, fn in bidders.items():
        try:
            b = fn(state)
            out[b.agent] = (b.bid_score, b.requested_hours)
        except Exception as e:
            out[name] = (None, f"ERR {e}")
    return out


def main():
    base_state = get_current_state()
    bidders = load_bidders()
    print(f"Agents found: {', '.join(bidders)}\n")
    print("Base state:", base_state, "\n")

    baseline = None
    for label, fn in SCENARIOS:
        s = fn(clone(base_state))
        bids = collect(s, bidders)
        if baseline is None:
            baseline = bids
        print(f"== {label}")
        for agent, (score, hours) in bids.items():
            if score is None:
                print(f"   {agent:<18} {hours}")
                continue
            b_score = baseline.get(agent, (score, hours))[0]
            delta = round(score - b_score, 2)
            print(f"   {agent:<18} score={score:<5} hours={hours:<3} delta_vs_baseline={delta:+}")
        print()


if __name__ == "__main__":
    main()