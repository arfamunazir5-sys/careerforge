import json
import os
from typing import List

GRAPH_PATH = os.path.join(os.path.dirname(__file__), "skill_graph.json")


def _load_graph() -> dict:
    with open(GRAPH_PATH, "r") as f:
        return json.load(f)


def get_next_skill(target_role: str, completed_skills: List[str]) -> str:
    """Returns the next skill in the ordered chain for this role that
    the user hasn't completed yet, respecting prerequisite order."""
    graph = _load_graph()
    chain = graph.get(target_role, [])
    if not chain:
        return "general_skill_development"

    for skill in chain:
        if skill not in completed_skills:
            return skill

    return chain[-1]


def get_full_chain(target_role: str) -> List[str]:
    graph = _load_graph()
    return graph.get(target_role, [])