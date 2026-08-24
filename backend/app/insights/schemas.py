from pydantic import BaseModel
from typing import List


class ModuleScore(BaseModel):
    name: str
    score: int


class CareerHealthResult(BaseModel):
    overall_score: int
    modules: List[ModuleScore]


class ExplanationItem(BaseModel):
    agent: str
    hours: int
    explanation: str


class ExplainabilityResult(BaseModel):
    week_number: int
    items: List[ExplanationItem]