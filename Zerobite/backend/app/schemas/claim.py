from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ClaimCreate(BaseModel):
    donation_id: int = Field(gt=0)
    quantity: float = Field(gt=0, le=100000)


class ClaimPublic(BaseModel):
    id: int
    donation_id: int
    receiver_id: int
    quantity: float
    status: str
    match_score: float | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
