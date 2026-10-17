"""Read-only probe: prints FINAL hour allocation (through the real coordinator)
for each scenario. Reuses calibration_probe.py. Never writes mock_state.json.
Run from the backend folder:  python scripts\\allocation_probe.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import calibration_probe as cp
from app.agents.coordinator import allocate
from app.state.state_builder import get_current_state


def hours_for(state, bidders):
    bids = [fn(state) for fn in bidders.values()]
    alloc = allocate(state, bids)
    return {a.agent: a.hours for a in alloc.allocations}, {b.agent: b.bid_score for b in bids}


def main():
    base_state = get_current_state()
    bidders = cp.load_bidders()
    print(f"available_hours = {base_state.available_hours}\n")

    baseline = None
    for label, fn in cp.SCENARIOS:
        s = fn(cp.clone(base_state))
        hours, bids = hours_for(s, bidders)
        if baseline is None:
            baseline = hours
        print(f"== {label}   (total hours = {sum(hours.values())})")
        for agent in sorted(hours):
            d = hours[agent] - baseline.get(agent, hours[agent])
            print(f"   {agent:<16} bid={bids[agent]:<5} hours={hours[agent]:<3} change_vs_baseline={d:+d}")
        print()


if __name__ == "__main__":
    main()