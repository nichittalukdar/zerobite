from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationPublic(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    event_type: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
