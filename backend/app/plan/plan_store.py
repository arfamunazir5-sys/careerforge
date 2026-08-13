import json
import os
from app.plan.schemas import WeeklyPlan

PLAN_PATH = os.path.join(os.path.dirname(__file__), "weekly_plan.json")


def save_plan(plan: WeeklyPlan) -> None:
    with open(PLAN_PATH, "w") as f:
        json.dump(plan.dict(), f, indent=2)


def load_plan() -> WeeklyPlan:
    if not os.path.exists(PLAN_PATH):
        raise FileNotFoundError("No weekly plan generated yet. Call /generate-plan first.")
    with open(PLAN_PATH, "r") as f:
        data = json.load(f)
    return WeeklyPlan(**data)