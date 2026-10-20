from __future__ import annotations
from datetime import datetime, timezone
from app.core import Base
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    pending_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    password_hash: Mapped[str | None] = mapped_column(String(500), nullable=True)
    language: Mapped[str] = mapped_column(String(32), default="English")
    role: Mapped[str] = mapped_column(String(32), default="farmer")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
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
    reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )
    email_verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        "EmailVerificationToken", back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )