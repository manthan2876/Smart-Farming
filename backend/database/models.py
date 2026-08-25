from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    language: Mapped[str] = mapped_column(String(32), default="English")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    predictions: Mapped[list[Prediction]] = relationship(back_populates="user")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    raw_path: Mapped[str] = mapped_column(Text)
    processed_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    crop_conf: Mapped[float | None] = mapped_column(Float, nullable=True)
    disease: Mapped[str | None] = mapped_column(String(200), nullable=True)
    disease_conf: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(200), nullable=True)
    severity_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    result: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    user: Mapped[User] = relationship(back_populates="predictions")
    recommendation: Mapped[Recommendation | None] = relationship(back_populates="prediction", uselist=False, cascade="all, delete-orphan")
    feedback: Mapped[list[Feedback]] = relationship(back_populates="prediction", cascade="all, delete-orphan")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), unique=True)
    fertilizer: Mapped[str | None] = mapped_column(Text, nullable=True)
    pesticide: Mapped[str | None] = mapped_column(Text, nullable=True)
    irrigation: Mapped[str | None] = mapped_column(Text, nullable=True)
    prevention_tips: Mapped[str | None] = mapped_column(Text, nullable=True)

    prediction: Mapped[Prediction] = relationship(back_populates="recommendation")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), index=True)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    farmer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    prediction: Mapped[Prediction] = relationship(back_populates="feedback")
