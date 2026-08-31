from datetime import datetime, timezone
from app.core import Base
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class ExpertReview(Base):
    __tablename__ = "expert_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("predictions.id"), unique=True
    )
    expert_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(40), default="pending")
    decision: Mapped[str | None] = mapped_column(String(40), nullable=True)
    corrected_disease: Mapped[str | None] = mapped_column(String(200), nullable=True)
    corrected_severity: Mapped[float | None] = mapped_column(Float, nullable=True)
    farmer_guidance: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    prediction: Mapped["Prediction"] = relationship(back_populates="expert_review")
    expert: Mapped["User | None"] = relationship(
        back_populates="expert_reviews", foreign_keys=[expert_id]
    )