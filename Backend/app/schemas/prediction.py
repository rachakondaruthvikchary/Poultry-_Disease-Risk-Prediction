from datetime import datetime
from pydantic import BaseModel


class ImagePredictionResponse(BaseModel):
    id: int
    farm_id: int
    image_path: str
    disease_name: str
    confidence: float
    risk_level: str
    suggested_action: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RiskResponse(BaseModel):
    risk_score: float
    risk_category: str
