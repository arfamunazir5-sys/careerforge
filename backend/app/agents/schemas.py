from pydantic import BaseModel
from typing import List


class Bid(BaseModel):
    agent: str
    bid_score: float
    requested_hours: int
    reason: str


class AgentAllocation(BaseModel):
    agent: str
    hours: int


class Allocation(BaseModel):
    week_number: int
    allocations: List[AgentAllocation]