from pydantic import BaseModel


class Bid(BaseModel):
    agent: str
    bid_score: float
    requested_hours: int
    reason: str