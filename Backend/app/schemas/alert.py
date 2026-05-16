from datetime import datetime
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    farm_id: int
    title: str
    message: str
    severity: str
    source: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
