from fastapi import FastAPI, HTTPException
from app.state.state_builder import get_current_state
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate
from app.plan.plan_generator import generate_plan
from app.plan.plan_store import save_plan, load_plan
from app.tracker.progress_tracker import mark_task

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