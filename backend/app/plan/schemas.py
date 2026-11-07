from pydantic import BaseModel
from typing import List


class Task(BaseModel):
    id: str
    agent: str
    title: str
    hours: int
    status: str  # "pending", "done", "ignored"
    why: str = ""  # reasoning captured when the plan was built


class WeeklyPlan(BaseModel):
    week_number: int
    tasks: List[Task]