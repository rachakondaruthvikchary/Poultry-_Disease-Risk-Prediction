from sqlalchemy.orm import Session

from app.models.alert import Alert


def create_alert(
    db: Session,
    farm_id: int,
    title: str,
    message: str,
    severity: str,
    source: str,
) -> Alert:
    alert = Alert(
        farm_id=farm_id,
        title=title,
        message=message,
        severity=severity,
        source=source,
        is_read=False,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
