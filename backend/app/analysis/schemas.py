from pydantic import BaseModel
from typing import List


class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    target_role: str


class ResumeAnalysisResult(BaseModel):
    resume_score: int
    missing_skills: List[str]
    weak_sections: List[str]
    keyword_gaps: List[str]


class PortfolioScanRequest(BaseModel):
    github_username: str


class PortfolioScanResult(BaseModel):
    portfolio_score: int
    repo_count: int
    readme_ratio: float
    notes: List[str]