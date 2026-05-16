from sqlalchemy import Integer, Float, Date, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class DailyRecord(Base):
    __tablename__ = "daily_records"
    __table_args__ = (
        Index("ix_daily_records_farm_date", "farm_id", "record_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), index=True)
    record_date: Mapped[Date] = mapped_column(Date, index=True)
    temperature: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    feed_intake: Mapped[float] = mapped_column(Float)
    water_intake: Mapped[float] = mapped_column(Float)
    activity_level: Mapped[float] = mapped_column(Float)
    mortality_rate: Mapped[float] = mapped_column(Float)
    bird_age: Mapped[int] = mapped_column(Integer)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_category: Mapped[str] = mapped_column(default="Low", index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm", back_populates="daily_records")
