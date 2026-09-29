from app.state.schemas import StateVector
from app.insights.schemas import CareerHealthResult, ModuleScore, BiggestOpportunity
from app.agents.role_weights import get_weights_for_role

# Maps role_weights.py's agent keys onto the 4 health-score modules.
# skill_building maps to Resume as the closest existing numeric proxy for
# overall technical strength — there's no dedicated "skill score" field yet,
# so this reuses what's already in the schema rather than adding a new one.
AGENT_TO_MODULE = {
    "skill_building": "Resume",
    "portfolio": "Portfolio",
    "networking": "Networking",
    "interview_prep": "Interview",
}


def _get_label(score: int) -> str:
    if score <= 40:
        return "Needs Attention"
    elif score <= 60:
        return "Developing"
    elif score <= 80:
        return "Solid"
    return "Strong"


def compute_career_health(state: StateVector) -> CareerHealthResult:
    weights = get_weights_for_role(state.target_role)

    module_scores = {
        "Resume": state.resume_score,
        "Portfolio": state.portfolio_score,
        "Networking": state.networking_score,
        "Interview": state.interview_score,
    }
    modules = [ModuleScore(name=name, score=score) for name, score in module_scores.items()]

    weighted_sum = sum(
        module_scores[module_name] * weights.get(agent, 0.25)
        for agent, module_name in AGENT_TO_MODULE.items()
    )
    overall = round(weighted_sum)

    return CareerHealthResult(overall_score=overall, label=_get_label(overall), modules=modules)

NOTE_FIELD_MAP = {
    "Resume": "resume_notes",
    "Portfolio": "portfolio_notes",
}


def compute_biggest_opportunity(state: StateVector) -> BiggestOpportunity:
    modules = {
        "Resume": state.resume_score,
        "Portfolio": state.portfolio_score,
        "Networking": state.networking_score,
        "Interview": state.interview_score,
    }
    weakest_module = min(modules, key=modules.get)
    weakest_score = modules[weakest_module]

    note_field = NOTE_FIELD_MAP.get(weakest_module)
    note = getattr(state, note_field, "") if note_field else ""
    if not note:
        note = f"{weakest_module} is currently your lowest-scoring area for this role."

    return BiggestOpportunity(module=weakest_module, score=weakest_score, note=note)