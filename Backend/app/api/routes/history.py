from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.alert import Alert
from app.models.farm import Farm
from app.models.user import User
from app.services.export_service import to_csv, to_pdf

router = APIRouter()


@router.get("/{farm_id}")
def get_history(
    farm_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    query = db.query(Alert).filter(Alert.farm_id == farm_id).order_by(Alert.created_at.desc())
    total = query.count()
    alerts = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": alerts,
    }


@router.get("/{farm_id}/export/csv")
def export_history_csv(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    alerts = db.query(Alert).filter(Alert.farm_id == farm_id).order_by(Alert.created_at.desc()).all()
    rows = [
        {
            "Alert ID": a.id,
            "Title": a.title,
            "Message": a.message,
            "Severity": a.severity,
            "Source": a.source,
            "Status": "Seen",
            "Date": a.created_at.strftime('%Y-%m-%d'),
            "Time": a.created_at.strftime('%H:%M:%S'),
        }
        for a in alerts
    ]
    csv_data = to_csv(rows)
    return StreamingResponse(iter([csv_data]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=history.csv"})


@router.get("/{farm_id}/export/pdf")
def export_history_pdf(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    alerts = db.query(Alert).filter(Alert.farm_id == farm_id).order_by(Alert.created_at.desc()).all()
    rows = [
        {
            "Alert": a.title,
            "Severity": a.severity,
            "Source": a.source,
            "Status": "Seen",
            "Date": a.created_at.strftime('%b %d, %Y'),
            "Time": a.created_at.strftime('%I:%M %p'),
        }
        for a in alerts
    ]

    pdf_bytes = to_pdf("PoultryGuard AI - Alert History Report", rows)
    return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=history.pdf"})
