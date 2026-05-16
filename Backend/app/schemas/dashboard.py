from pydantic import BaseModel


class DashboardOverview(BaseModel):
    current_risk_level: str
    latest_image_prediction: str
    total_alerts: int
    farm_status: str


class TrendPoint(BaseModel):
    day: str
    risk_score: float
