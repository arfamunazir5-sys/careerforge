from app.state.schemas import StateVector
from app.insights.schemas import CareerHealthResult, ModuleScore


def compute_career_health(state: StateVector) -> CareerHealthResult:
    modules = [
        ModuleScore(name="Resume", score=state.resume_score),
        ModuleScore(name="Portfolio", score=state.portfolio_score),
        ModuleScore(name="Networking", score=state.networking_score),
        ModuleScore(name="Interview", score=state.interview_score),
    ]
    overall = round(sum(m.score for m in modules) / len(modules))
    return CareerHealthResult(overall_score=overall, modules=modules)