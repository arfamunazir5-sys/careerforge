import os
from typing import Dict, List, Optional
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.state.state_builder import get_current_state, reset_state, update_state_fields
from app.analysis.schemas import ResumeAnalysisRequest, PortfolioScanRequest
from app.analysis.resume_analyzer import analyze_resume
from app.analysis.portfolio_scanner import scan_portfolio, PortfolioScanError
from app.analysis.pdf_text import extract_text_from_pdf, PdfExtractionError, MAX_BYTES
from app.analysis.self_assessment import (
    AssessmentError,
    public_questions,
    score_interview,
    score_networking,
)
from app.analysis.skill_graph import get_next_skill, get_full_chain
from app.roles import role_options, portfolio_mode, NEUTRAL_PORTFOLIO_SCORE
from app.analysis.portfolio_evidence import score_portfolio_evidence, EvidenceError
from app.insights.role_simulator import simulate_all_roles
from app.insights.weekly import summarize_week, close_week
from app.agents.learning import summarize_learning
from app.agents.role_weights import ROLE_WEIGHTS
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate, compute_shares
from app.plan.plan_generator import generate_plan
from app.plan.plan_store import save_plan, load_plan, clear_plan
from app.tracker.progress_tracker import mark_task
from app.tracker.reward_log import get_log, clear_log
from app.export.calendar_export import build_ics_content
from app.insights.career_health import compute_career_health, compute_biggest_opportunity
from app.insights.explainability import generate_explanations
from app.insights.adaptation import snapshot_update, compute_adaptation

class ProfileUpdateRequest(BaseModel):
    target_role: str
    available_hours: int


class EvidenceRequest(BaseModel):
    links: List[str] = []
    case_studies: int = 0
    has_results: bool = False
    has_process: bool = False
    recent_work: bool = False


class NextWeekRequest(BaseModel):
    available_hours: Optional[int] = None
    confidence: Optional[int] = None


class AssessmentRequest(BaseModel):
    interview_answers: Optional[Dict[str, int]] = None
    networking_answers: Optional[Dict[str, int]] = None
    confidence: Optional[int] = None

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


def _require_known_role(role: str) -> None:
    if role not in ROLE_WEIGHTS:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown target role '{role}'. Choose one of: {', '.join(ROLE_WEIGHTS)}.",
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
    clear_plan()
    clear_log()

    return {
        "status": "reset",
        "message": "CareerForge state, weekly plan and reward log restored to baseline."
    }

@app.get("/bids")
def read_bids():
    return _get_bids(get_current_state())


@app.get("/allocate")
def read_allocation():
    state = get_current_state()
    return allocate(state, _get_bids(state))


def _build_and_store_plan(state):
    """Builds this week's plan (with the reasoning for each task), saves it and
    stores the allocation snapshot used by the Adaptation panel."""
    bids = _get_bids(state)
    allocation = allocate(state, bids)
    explanations = generate_explanations(state, bids, allocation)
    why_by_agent = {item.agent: item.explanation for item in explanations.items}
    plan = generate_plan(state, allocation, why_by_agent)
    save_plan(plan)
    update_state_fields(snapshot_update(state, allocation, compute_shares(state, bids)))
    return plan


@app.post("/generate-plan")
def create_plan():
    return _build_and_store_plan(get_current_state())


@app.get("/week-summary")
def read_week_summary():
    state = get_current_state()
    try:
        plan = load_plan()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No weekly plan yet. Call POST /generate-plan first.")
    return summarize_week(state, plan)


@app.post("/next-week")
def start_next_week(payload: NextWeekRequest):
    if payload.available_hours is not None and not 1 <= payload.available_hours <= 80:
        raise HTTPException(status_code=422, detail="available_hours must be between 1 and 80.")
    if payload.confidence is not None and not 1 <= payload.confidence <= 10:
        raise HTTPException(status_code=422, detail="confidence must be between 1 and 10.")

    state = get_current_state()
    try:
        plan = load_plan()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No weekly plan yet. Call POST /generate-plan first.")

    updates, summary = close_week(state, plan, payload.available_hours, payload.confidence)
    update_state_fields(updates)
    new_state = get_current_state()
    new_plan = _build_and_store_plan(new_state)
    return {"closed": summary, "week_number": new_state.week_number, "plan": new_plan}


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
    _require_known_role(payload.target_role)
    if not 1 <= payload.available_hours <= 80:
        raise HTTPException(status_code=422, detail="available_hours must be between 1 and 80.")

    state = get_current_state()
    next_skill = get_next_skill(payload.target_role, state.skill_progress.completed_skills)

    updates = {
        "target_role": payload.target_role,
        "available_hours": payload.available_hours,
        "profile_completed": True,
        "skill_progress": {
            "completed_skills": state.skill_progress.completed_skills,
            "next_skill": next_skill,
        },
    }
    if payload.target_role != state.target_role:
        # The resume notes, quiz result and in-progress skill tasks belonged to the old role.
        updates["resume_notes"] = ""
        updates["resume_details"] = {}
        updates["skill_task_progress"] = 0
        assessment = dict(state.assessment or {})
        assessment.pop("interview", None)
        updates["assessment"] = assessment
        if portfolio_mode(payload.target_role) != portfolio_mode(state.target_role):
            # a GitHub score and an evidence score are not comparable
            updates["portfolio_details"] = {}
            updates["portfolio_notes"] = ""
            updates["portfolio_score"] = NEUTRAL_PORTFOLIO_SCORE
    update_state_fields(updates)
    return get_current_state()


@app.get("/roles")
def read_roles():
    return role_options()


@app.get("/simulate-roles")
def read_role_simulation():
    return simulate_all_roles(get_current_state())


@app.get("/self-assessment/questions")
def read_assessment_questions():
    state = get_current_state()
    try:
        return public_questions(state.target_role)
    except AssessmentError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/self-assessment")
def submit_assessment(payload: AssessmentRequest):
    if (
        payload.interview_answers is None
        and payload.networking_answers is None
        and payload.confidence is None
    ):
        raise HTTPException(status_code=422, detail="Nothing to assess. Answer at least one section.")

    state = get_current_state()
    updates = {}
    assessment = dict(state.assessment or {})
    new_scores = {}
    summary = {"interview": None, "networking": None, "confidence": None}

    try:
        if payload.interview_answers is not None:
            result = score_interview(state.target_role, payload.interview_answers)
            updates["interview_score"] = result["score"]
            new_scores["Interview"] = result["score"]
            assessment["interview"] = {"role": state.target_role, **result}
            summary["interview"] = result
        if payload.networking_answers is not None:
            result = score_networking(payload.networking_answers)
            updates["networking_score"] = result["score"]
            new_scores["Networking"] = result["score"]
            assessment["networking"] = result
            summary["networking"] = result
    except AssessmentError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if payload.confidence is not None:
        if not 1 <= payload.confidence <= 10:
            raise HTTPException(status_code=422, detail="confidence must be between 1 and 10.")
        updates["confidence"] = payload.confidence
        assessment["confidence"] = payload.confidence
        summary["confidence"] = payload.confidence

    # A measured score is not progress: move the plan snapshot with it so the
    # Adaptation panel only reports progress that came from completed tasks.
    snapshot = dict(state.plan_snapshot or {})
    if snapshot.get("scores") and new_scores:
        snapshot["scores"] = {**snapshot["scores"], **new_scores}
        updates["plan_snapshot"] = snapshot

    updates["assessment"] = assessment
    update_state_fields(updates)
    return summary

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
    shares = compute_shares(state, bids)

    return {
        "career_health": career_health,
        "explanations": explanations,
        "biggest_opportunity": biggest_opportunity,
        "bids": bids,
        "allocation": allocation,
        "adaptation": compute_adaptation(state, shares),
        "allocation_shares": shares,
        "agent_learning": summarize_learning(state),
    },

@app.post("/analyze-resume")
def analyze_resume_endpoint(payload: ResumeAnalysisRequest):
    _require_known_role(payload.target_role)
    result = analyze_resume(payload.resume_text, payload.target_role)
    if result.missing_skills:
        resume_note = f"Missing from resume: {', '.join(result.missing_skills)}"
    else:
        resume_note = "Resume covers the key skills for this role"
    update_state_fields({
        "resume_score": result.resume_score,
        "resume_notes": resume_note,
        "resume_details": {
            "role": payload.target_role,
            "missing_skills": result.missing_skills,
            "weak_sections": result.weak_sections,
            "keyword_gaps": result.keyword_gaps,
        },
    })
    return result


@app.post("/extract-resume-text")
async def extract_resume_text(file: UploadFile = File(...)):
    """Reads the text from an uploaded PDF resume. The file and text are not stored."""
    data = await file.read(MAX_BYTES + 1)
    try:
        return extract_text_from_pdf(data)
    except PdfExtractionError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.post("/portfolio-evidence")
def submit_portfolio_evidence(payload: EvidenceRequest):
    """For roles without a GitHub portfolio: scores links and a short checklist (self-reported)."""
    state = get_current_state()
    if portfolio_mode(state.target_role) != "evidence":
        raise HTTPException(status_code=422, detail="This role uses a GitHub scan. Use the GitHub username instead.")
    try:
        result = score_portfolio_evidence(
            payload.links, payload.case_studies, payload.has_results, payload.has_process, payload.recent_work
        )
    except EvidenceError as e:
        raise HTTPException(status_code=422, detail=str(e))
    update_state_fields({
        "portfolio_score": result["score"],
        "portfolio_notes": "; ".join(result["notes"]),
        "portfolio_details": {
            "mode": "evidence",
            "links": result["links"],
            "case_studies": result["case_studies"],
            "has_results": result["has_results"],
            "has_process": result["has_process"],
            "recent_work": result["recent_work"],
            "notes": result["notes"],
        },
    })
    return result


@app.post("/analyze-portfolio")
def analyze_portfolio_endpoint(payload: PortfolioScanRequest):
    if portfolio_mode(get_current_state().target_role) == "evidence":
        raise HTTPException(status_code=422, detail="This role uses portfolio evidence instead of a GitHub scan.")
    try:
        result = scan_portfolio(payload.github_username)
    except PortfolioScanError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    portfolio_note = "; ".join(result.notes) if result.notes else "Portfolio scan complete"
    update_state_fields({
        "portfolio_score": result.portfolio_score,
        "portfolio_notes": portfolio_note,
        "portfolio_details": {
            "repo_count": result.repo_count,
            "readme_ratio": result.readme_ratio,
            "notes": result.notes,
        },
    })
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