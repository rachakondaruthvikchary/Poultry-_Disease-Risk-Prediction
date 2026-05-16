from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.farm import Farm
from app.models.daily_record import DailyRecord
from app.schemas.record import DailyRecordCreate, DailyRecordResponse
from app.services.risk_model_service import risk_predictor
from app.services.alert_service import create_alert

router = APIRouter()


@router.post("", response_model=DailyRecordResponse)
def create_record(payload: DailyRecordCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farm = db.query(Farm).filter(Farm.id == payload.farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    result = risk_predictor.predict(
        [
            payload.temperature,
            payload.humidity,
            payload.feed_intake,
            payload.water_intake,
            payload.activity_level,
            payload.mortality_rate,
            payload.bird_age,
        ]
    )

    record = DailyRecord(
        farm_id=payload.farm_id,
        record_date=payload.record_date,
        temperature=payload.temperature,
        humidity=payload.humidity,
        feed_intake=payload.feed_intake,
        water_intake=payload.water_intake,
        activity_level=payload.activity_level,
        mortality_rate=payload.mortality_rate,
        bird_age=payload.bird_age,
        risk_score=result["risk_score"],
        risk_category=result["risk_category"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    if result["risk_category"] == "High":
        create_alert(
            db,
            payload.farm_id,
            "High Structured Risk Detected",
            f"Risk score {result['risk_score']} from latest structured farm metrics.",
            "High",
            "structured_risk",
        )

    return record


@router.get("/{farm_id}", response_model=list[DailyRecordResponse])
def list_records(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    return (
        db.query(DailyRecord)
        .filter(DailyRecord.farm_id == farm_id)
        .order_by(DailyRecord.record_date.desc())
        .limit(90)
        .all()
    )
