from __future__ import annotations
from datetime import datetime, timezone
from app.core import Base
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(500), nullable=True)
    language: Mapped[str] = mapped_column(String(32), default="English")
    role: Mapped[str] = mapped_column(String(32), default="farmer")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

    predictions: Mapped[list["Prediction"]] = relationship(back_populates="user")
    farm: Mapped["Farm | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    images: Mapped[list["Image"]] = relationship(back_populates="user")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user")
    expert_reviews: Mapped[list["ExpertReview"]] = relationship(
        back_populates="expert", foreign_keys="ExpertReview.expert_id"
    )