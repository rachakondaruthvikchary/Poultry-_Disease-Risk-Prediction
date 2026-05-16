"""
Dashboard API Routes
Provides endpoints for retrieving farm dashboard data, including risk assessments,
predictions, trends, and alerts.
"""

from collections import defaultdict
from datetime import datetime, timedelta, date
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.alert import Alert
from app.models.daily_record import DailyRecord
from app.models.farm import Farm
from app.models.image_prediction import ImagePrediction
from app.models.user import User

# ============================================================================
# Constants
# ============================================================================

RISK_TO_SCORE = {
    "Low": 0.2,
    "Medium": 0.5,
    "High": 0.75,
    "Critical": 0.95,
}

RISK_RANK = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4,
}

RISK_STATUS_MAP = {
    "Critical": "Critical",
    "High": "Critical",
    "Medium": "Warning",
    "Low": "Stable",
}

TREND_DAYS = 14

# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter()

# ============================================================================
# Utility Functions
# ============================================================================


def _risk_rank(level: str) -> int:
    """Get numeric rank for risk level (higher = more severe)."""
    return RISK_RANK.get(level, 1)


def _status_from_risk(level: str) -> str:
    """Map risk level to farm status."""
    return RISK_STATUS_MAP.get(level, "Stable")


def _get_farm_or_404(farm_id: int, user_id: int, db: Session) -> Farm:
    """Retrieve farm and raise 404 if not found or not owned by user."""
    farm = db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.user_id == user_id
    ).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


def _get_latest_record_and_prediction(
    farm_id: int, db: Session
) -> tuple[DailyRecord | None, ImagePrediction | None]:
    """Fetch latest daily record and image prediction for a farm."""
    latest_record = (
        db.query(DailyRecord)
        .filter(DailyRecord.farm_id == farm_id)
        .order_by(DailyRecord.record_date.desc())
        .first()
    )
    latest_prediction = (
        db.query(ImagePrediction)
        .filter(ImagePrediction.farm_id == farm_id)
        .order_by(ImagePrediction.created_at.desc())
        .first()
    )
    return latest_record, latest_prediction


def _compute_risk_trend(
    farm_id: int, start: date, db: Session
) -> List[Dict[str, Any]]:
    """Compute 14-day risk trend from daily records and predictions."""
    daily_rows = (
        db.query(DailyRecord)
        .filter(DailyRecord.farm_id == farm_id, DailyRecord.record_date >= start)
        .order_by(DailyRecord.record_date.asc())
        .all()
    )
    prediction_rows = (
        db.query(ImagePrediction)
        .filter(
            ImagePrediction.farm_id == farm_id,
            ImagePrediction.created_at >= datetime.combine(start, datetime.min.time()),
        )
        .order_by(ImagePrediction.created_at.asc())
        .all()
    )

    # Aggregate risk scores by day
    bucket: Dict[str, List[float]] = defaultdict(list)
    for row in daily_rows:
        bucket[row.record_date.isoformat()].append(float(row.risk_score))

    for row in prediction_rows:
        day_key = row.created_at.date().isoformat()
        bucket[day_key].append(RISK_TO_SCORE.get(row.risk_level, 0.2))

    # Build trend with 14 days
    trend = []
    for offset in range(TREND_DAYS):
        day = (start + timedelta(days=offset)).isoformat()
        values = bucket.get(day, [])
        if values:
            score = round(sum(values) / len(values), 4)
            trend.append({
                "day": day,
                "risk_score": score,
                "has_data": True
            })
        else:
            # Return None for gaps to show visually in chart
            trend.append({
                "day": day,
                "risk_score": None,
                "has_data": False
            })

    return trend


def _determine_current_risk(
    latest_record: DailyRecord | None,
    latest_prediction: ImagePrediction | None
) -> str:
    """Determine the current risk level from latest data."""
    current_risk = "Low"
    if latest_record:
        current_risk = latest_record.risk_category
    if latest_prediction and _risk_rank(latest_prediction.risk_level) >= _risk_rank(current_risk):
        current_risk = latest_prediction.risk_level
    return current_risk

# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/{farm_id}")
def farm_dashboard(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive farm dashboard data.

    Includes:
    - Current risk level and farm status
    - Latest disease prediction
    - Total active alerts
    - 14-day risk trend

    Args:
        farm_id: The farm ID
        db: Database session
        current_user: Authenticated user (must own the farm)

    Returns:
        Dashboard data with overview and trend

    Raises:
        HTTPException: 404 if farm not found or not owned by user
    """
    # Validate farm ownership
    _get_farm_or_404(farm_id, current_user.id, db)

    # Fetch latest data
    latest_record, latest_prediction = _get_latest_record_and_prediction(farm_id, db)
    total_alerts = db.query(Alert).filter(Alert.farm_id == farm_id).count()

    # Compute 14-day trend for the current window first.
    # If no points exist in the current window, fall back to the latest
    # historical 14-day window so the chart still provides context.
    today = datetime.utcnow().date()
    start = today - timedelta(days=TREND_DAYS - 1)
    trend = _compute_risk_trend(farm_id, start, db)

    if not any(point.get("has_data") for point in trend):
        latest_dates = []
        if latest_record is not None:
            latest_dates.append(latest_record.record_date)
        if latest_prediction is not None:
            latest_dates.append(latest_prediction.created_at.date())

        if latest_dates:
            latest_activity = max(latest_dates)
            fallback_start = latest_activity - timedelta(days=TREND_DAYS - 1)
            trend = _compute_risk_trend(farm_id, fallback_start, db)

    # Determine current risk
    current_risk = _determine_current_risk(latest_record, latest_prediction)

    # Compute a numeric current risk score for UI (0-1). Prefer latest structured
    # daily record score when available, otherwise use mapped score for image prediction.
    current_risk_score = None
    if latest_record:
        try:
            current_risk_score = float(latest_record.risk_score)
        except Exception:
            current_risk_score = None
    if latest_prediction:
        pred_score = RISK_TO_SCORE.get(latest_prediction.risk_level, RISK_TO_SCORE.get("Medium", 0.5))
        if current_risk_score is None or pred_score > current_risk_score:
            current_risk_score = pred_score
    if current_risk_score is None:
        current_risk_score = RISK_TO_SCORE.get(current_risk, 0.2)

    return {
        "overview": {
            "current_risk_level": current_risk,
            "current_risk_score": current_risk_score,
            "latest_image_prediction": (
                latest_prediction.disease_name if latest_prediction else "No prediction"
            ),
            "total_alerts": total_alerts,
            "farm_status": _status_from_risk(current_risk),
        },
        "trend": trend,
    }
