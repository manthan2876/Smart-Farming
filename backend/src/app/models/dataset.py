from datetime import datetime, timezone
from app.core import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class DatasetCandidate(Base):
    __tablename__ = "dataset_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), index=True, unique=True)
    source: Mapped[str] = mapped_column(String(50)) # 'farmer_rejection' or 'expert_correction'
    original_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    corrected_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    image_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="pending_review") # pending_review, added_to_dataset, rejected
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    prediction: Mapped["Prediction"] = relationship()
