from datetime import date, datetime
from pydantic import BaseModel, Field


class DailyRecordCreate(BaseModel):
    farm_id: int
    record_date: date
    temperature: float = Field(ge=-10, le=60)
    humidity: float = Field(ge=0, le=100)
    feed_intake: float = Field(gt=0)
    water_intake: float = Field(gt=0)
    activity_level: float = Field(ge=0, le=100)
    mortality_rate: float = Field(ge=0, le=100)
    bird_age: int = Field(ge=1, le=500)


class DailyRecordResponse(BaseModel):
    id: int
    farm_id: int
    record_date: date
    temperature: float
    humidity: float
    feed_intake: float
    water_intake: float
    activity_level: float
    mortality_rate: float
    bird_age: int
    risk_score: float
    risk_category: str
    created_at: datetime

    model_config = {"from_attributes": True}
