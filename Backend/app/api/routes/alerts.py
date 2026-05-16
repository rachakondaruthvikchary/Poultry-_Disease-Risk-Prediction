from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.alert import Alert
from app.models.farm import Farm
from app.models.user import User
from app.schemas.alert import AlertResponse

router = APIRouter()


@router.get("/{farm_id}", response_model=list[AlertResponse])
def list_alerts(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    return db.query(Alert).filter(Alert.farm_id == farm_id).order_by(Alert.created_at.desc()).limit(100).all()


@router.patch("/{alert_id}/read", response_model=AlertResponse)
def mark_alert_read(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = (
        db.query(Alert)
        .join(Farm, Farm.id == Alert.farm_id)
        .filter(Alert.id == alert_id, Farm.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return alert
