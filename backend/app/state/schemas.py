from pydantic import BaseModel
from typing import List


class SkillProgress(BaseModel):
    completed_skills: List[str]
    next_skill: str


class StateVector(BaseModel):
    user_id: str
    target_role: str
    week_number: int
    available_hours: int
    completed_tasks_last_week: int
    ignored_tasks_last_week: int
    confidence: int
    interview_score: int
    resume_score: int
    networking_score: int
    portfolio_score: int
    streak_count: int
    skill_progress: SkillProgress