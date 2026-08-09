from fastapi import FastAPI
from app.state.state_builder import get_current_state
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "CareerForge backend is alive"}


@app.get("/state")
def read_state():
    return get_current_state()


@app.get("/bids")
def read_bids():
    state = get_current_state()
    return [
        skill_agent.get_bid(state),
        networking_agent.get_bid(state),
        portfolio_agent.get_bid(state),
        interview_agent.get_bid(state),
    ]