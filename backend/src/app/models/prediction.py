from datetime import datetime, timezone
from typing import Any
from app.core import Base
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    plot_id: Mapped[int | None] = mapped_column(
        ForeignKey("plots.id"), nullable=True, index=True
    )
    image_id: Mapped[int | None] = mapped_column(ForeignKey("images.id"), nullable=True)
    raw_path: Mapped[str] = mapped_column(Text)
    processed_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    crop_conf: Mapped[float | None] = mapped_column(Float, nullable=True)
    disease: Mapped[str | None] = mapped_column(String(200), nullable=True)
    disease_conf: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(200), nullable=True)
    severity_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ready")
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("predictions.id"), nullable=True, index=True)
    result: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="predictions")
    plot: Mapped["Plot | None"] = relationship(back_populates="predictions")
    image: Mapped["Image | None"] = relationship(back_populates="prediction")
    recommendation: Mapped["Recommendation | None"] = relationship(
        back_populates="prediction", uselist=False, cascade="all, delete-orphan"
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        back_populates="prediction", cascade="all, delete-orphan"
    )
    expert_review: Mapped["ExpertReview | None"] = relationship(
        back_populates="prediction", uselist=False, cascade="all, delete-orphan"
    )
    parent: Mapped["Prediction | None"] = relationship(
        "Prediction", remote_side="[Prediction.id]", backref="follow_ups"
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="prediction")
