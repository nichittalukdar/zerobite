from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class DeliveryAssign(BaseModel):
    volunteer_id: int = Field(gt=0)


class DeliveryPublic(BaseModel):
    id: int
    claim_id: int
    volunteer_id: int | None
    status: str
    picked_up_at: datetime | None
    delivered_at: datetime | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


DeliveryStatus = Literal["picked_up", "delivered", "cancelled"]


class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus
