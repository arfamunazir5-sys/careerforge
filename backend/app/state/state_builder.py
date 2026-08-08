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