import json
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), "reward_log.json")


def _load_log() -> list:
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r") as f:
        return json.load(f)


def append_reward(entry: dict) -> None:
    log = _load_log()
    log.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def get_log() -> list:
    return _load_log()


def clear_log() -> None:
    """Deletes the reward log (used by /reset)."""
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)