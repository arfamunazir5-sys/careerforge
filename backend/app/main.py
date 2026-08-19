from fastapi import FastAPI, HTTPException
from app.state.state_builder import get_current_state, update_state_fields
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate
from app.plan.plan_generator import generate_plan
from app.plan.plan_store import save_plan, load_plan
from app.tracker.progress_tracker import mark_task
from app.tracker.reward_log import get_log
from app.analysis.schemas import ResumeAnalysisRequest, PortfolioScanRequest
from app.analysis.resume_analyzer import analyze_resume
from app.analysis.portfolio_scanner import scan_portfolio
from app.analysis.skill_graph import get_next_skill, get_full_chain

app = FastAPI()


def _get_bids(state):
    return [
        skill_agent.get_bid(state),
        networking_agent.get_bid(state),
        portfolio_agent.get_bid(state),
        interview_agent.get_bid(state),
    ]


@app.get("/")
def read_root():
    return {"status": "CareerForge backend is alive"}


@app.get("/state")
def read_state():
    return get_current_state()


@app.get("/bids")
def read_bids():
    return _get_bids(get_current_state())


@app.get("/allocate")
def read_allocation():
    state = get_current_state()
    return allocate(state, _get_bids(state))


@app.post("/generate-plan")
def create_plan():
    state = get_current_state()
    allocation = allocate(state, _get_bids(state))
    plan = generate_plan(state, allocation)
    save_plan(plan)
    return plan


@app.get("/plan")
def read_plan():
    try:
        return load_plan()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No weekly plan yet. Call POST /generate-plan first.")


@app.post("/tasks/{task_id}/complete")
def complete_task(task_id: str):
    try:
        return mark_task(task_id, "done")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/tasks/{task_id}/ignore")
def ignore_task(task_id: str):
    try:
        return mark_task(task_id, "ignored")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/rewards")
def read_rewards():
    return get_log()


@app.post("/analyze-resume")
def analyze_resume_endpoint(payload: ResumeAnalysisRequest):
    result = analyze_resume(payload.resume_text, payload.target_role)
    update_state_fields({"resume_score": result.resume_score})
    return result


@app.post("/analyze-portfolio")
def analyze_portfolio_endpoint(payload: PortfolioScanRequest):
    result = scan_portfolio(payload.github_username)
    update_state_fields({"portfolio_score": result.portfolio_score})
    return result


@app.get("/skill-graph/{target_role}")
def read_skill_graph(target_role: str):
    return {"target_role": target_role, "chain": get_full_chain(target_role)}


@app.get("/skill-progress")
def read_skill_progress():
    state = get_current_state()
    next_skill = get_next_skill(state.target_role, state.skill_progress.completed_skills)
    return {
        "target_role": state.target_role,
        "completed_skills": state.skill_progress.completed_skills,
        "next_skill": next_skill,
        "full_chain": get_full_chain(state.target_role),
    }