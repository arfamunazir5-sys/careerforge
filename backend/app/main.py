import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.state.state_builder import get_current_state, reset_state, update_state_fields
from app.analysis.schemas import ResumeAnalysisRequest, PortfolioScanRequest
from app.analysis.resume_analyzer import analyze_resume
from app.analysis.portfolio_scanner import scan_portfolio
from app.analysis.skill_graph import get_next_skill, get_full_chain
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate
from app.plan.plan_generator import generate_plan
from app.plan.plan_store import save_plan, load_plan
from app.tracker.progress_tracker import mark_task
from app.tracker.reward_log import get_log
from app.export.calendar_export import build_ics_content
from app.insights.career_health import compute_career_health, compute_biggest_opportunity
from app.insights.explainability import generate_explanations

class ProfileUpdateRequest(BaseModel):
    target_role: str
    available_hours: int

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://careerforge-five-tau.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

@app.post("/reset")
def reset():

    reset_state()

    return {
        "status": "reset",
        "message": "CareerForge state restored to baseline."
    }

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

@app.get("/export-calendar")
def export_calendar():

    try:
        plan = load_plan()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="No weekly plan yet. Call POST /generate-plan first."
        )

    tasks = [task.model_dump() for task in plan.tasks]

    ics_content = build_ics_content(tasks)

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=careerforge_weekly_plan.ics"
        },
    )

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

@app.post("/update-profile")
def update_profile(payload: ProfileUpdateRequest):
    update_state_fields({
        "target_role": payload.target_role,
        "available_hours": payload.available_hours,
    })
    return get_current_state()

@app.get("/dashboard")
def read_dashboard():

    state = get_current_state()

    bids = _get_bids(state)

    allocation = allocate(state, bids)

    career_health = compute_career_health(state)

    explanations = generate_explanations(
        state,
        bids,
        allocation
    )

    biggest_opportunity = compute_biggest_opportunity(state)

    return {
        "career_health": career_health,
        "explanations": explanations,
        "biggest_opportunity": biggest_opportunity,
        "bids": bids,
        "allocation": allocation,
    }

@app.post("/analyze-resume")
def analyze_resume_endpoint(payload: ResumeAnalysisRequest):
    result = analyze_resume(payload.resume_text, payload.target_role)
    if result.missing_skills:
        resume_note = f"Missing from resume: {', '.join(result.missing_skills)}"
    else:
        resume_note = "Resume covers the key skills for this role"
    update_state_fields({"resume_score": result.resume_score, "resume_notes": resume_note})
    return result


@app.post("/analyze-portfolio")
def analyze_portfolio_endpoint(payload: PortfolioScanRequest):
    result = scan_portfolio(payload.github_username)
    portfolio_note = "; ".join(result.notes) if result.notes else "Portfolio scan complete"
    update_state_fields({"portfolio_score": result.portfolio_score, "portfolio_notes": portfolio_note})
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