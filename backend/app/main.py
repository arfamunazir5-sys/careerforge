from fastapi import FastAPI
from app.state.state_builder import get_current_state

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "CareerForge backend is alive"}


@app.get("/state")
def read_state():
    return get_current_state()