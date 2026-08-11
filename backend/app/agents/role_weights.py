ROLE_WEIGHTS = {
    "swe_backend": {
        "skill_building": 0.40,
        "portfolio": 0.25,
        "networking": 0.15,
        "interview_prep": 0.20,
    },
    "data_analyst": {
        "skill_building": 0.45,
        "portfolio": 0.20,
        "networking": 0.15,
        "interview_prep": 0.20,
    },
    "frontend_dev": {
        "skill_building": 0.35,
        "portfolio": 0.30,
        "networking": 0.15,
        "interview_prep": 0.20,
    },
}

DEFAULT_WEIGHTS = {
    "skill_building": 0.35,
    "portfolio": 0.25,
    "networking": 0.15,
    "interview_prep": 0.25,
}


def get_weights_for_role(target_role: str) -> dict:
    """Returns the priority weight profile for a given target role.
    Falls back to a balanced default if the role isn't in our list yet."""
    return ROLE_WEIGHTS.get(target_role, DEFAULT_WEIGHTS)