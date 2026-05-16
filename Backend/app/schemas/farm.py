from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class FarmCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=2, max_length=160)
    flock_size: int = Field(ge=1)


class FarmUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    location: Optional[str] = Field(default=None, min_length=2, max_length=160)
    flock_size: Optional[int] = Field(default=None, ge=1)


class FarmResponse(BaseModel):
    id: int
    user_id: int
    name: str
    location: str
    flock_size: int
    created_at: datetime

    model_config = {"from_attributes": True}
