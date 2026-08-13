from pydantic import BaseModel
from typing import List


class Task(BaseModel):
    id: str
    agent: str
    title: str
    hours: int
    status: str  # "pending", "done", "ignored"


class WeeklyPlan(BaseModel):
    week_number: int
    tasks: List[Task]