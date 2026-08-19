import json
import os
from app.state.schemas import StateVector

MOCK_STATE_PATH = os.path.join(os.path.dirname(__file__), "mock_state.json")


def get_current_state() -> StateVector:
    """
    For now, reads fake data from mock_state.json.
    Later, this function is the ONLY place that changes
    when we plug in real resume/portfolio data — nothing
    downstream needs to know the difference.
    """
    with open(MOCK_STATE_PATH, "r") as f:
        data = json.load(f)
    return StateVector(**data)
def update_state_fields(updates: dict) -> None:
    """Merges given fields into mock_state.json. Used by leaf modules
    (resume analyzer, portfolio scanner) to write real analysis results
    back into shared state, without those modules needing to know
    anything about the file format."""
    with open(MOCK_STATE_PATH, "r") as f:
        data = json.load(f)

    data.update(updates)

    with open(MOCK_STATE_PATH, "w") as f:
        json.dump(data, f, indent=2)