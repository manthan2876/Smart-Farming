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
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(500), nullable=True)
    language: Mapped[str] = mapped_column(String(32), default="English")
    role: Mapped[str] = mapped_column(String(32), default="farmer")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    predictions: Mapped[list[Prediction]] = relationship(back_populates="user")
    farm: Mapped[Farm | None] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    images: Mapped[list[Image]] = relationship(back_populates="user")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user")
    expert_reviews: Mapped[list["ExpertReview"]] = relationship(
        back_populates="expert", foreign_keys="ExpertReview.expert_id"
    )


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    area_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    crop_history: Mapped[list[str]] = mapped_column(JSON, default=list)

    user: Mapped[User] = relationship(back_populates="farm")
    plots: Mapped[list["Plot"]] = relationship(
        back_populates="farm", cascade="all, delete-orphan"
    )


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    raw_path: Mapped[str] = mapped_column(Text)
    processed_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    blur_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    brightness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    leaf_detected: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="images")
    prediction: Mapped[Prediction | None] = relationship(
        back_populates="image", uselist=False
    )


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
    result: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True
    )

    user: Mapped[User] = relationship(back_populates="predictions")
    plot: Mapped["Plot | None"] = relationship(back_populates="predictions")
    image: Mapped[Image | None] = relationship(back_populates="prediction")
    recommendation: Mapped[Recommendation | None] = relationship(
        back_populates="prediction", uselist=False, cascade="all, delete-orphan"
    )
    feedback: Mapped[list[Feedback]] = relationship(
        back_populates="prediction", cascade="all, delete-orphan"
    )
    expert_review: Mapped["ExpertReview | None"] = relationship(
        back_populates="prediction", uselist=False, cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="prediction")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("predictions.id"), unique=True
    )
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    prediction: Mapped[Prediction] = relationship(back_populates="feedback")


class Plot(Base):
    __tablename__ = "plots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    area_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="healthy")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    farm: Mapped[Farm] = relationship(back_populates="plots")
    predictions: Mapped[list[Prediction]] = relationship(back_populates="plot")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="plot")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    prediction_id: Mapped[int | None] = mapped_column(
        ForeignKey("predictions.id"), nullable=True, index=True
    )
    plot_id: Mapped[int | None] = mapped_column(
        ForeignKey("plots.id"), nullable=True, index=True
    )
    kind: Mapped[str] = mapped_column(String(40))
    severity: Mapped[str] = mapped_column(String(32), default="medium")
    title: Mapped[str] = mapped_column(String(240))
    body: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True
    )

    user: Mapped[User] = relationship(back_populates="alerts")
    prediction: Mapped[Prediction | None] = relationship(back_populates="alerts")
    plot: Mapped[Plot | None] = relationship(back_populates="alerts")


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
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    prediction: Mapped[Prediction] = relationship(back_populates="expert_review")
    expert: Mapped[User | None] = relationship(
        back_populates="expert_reviews", foreign_keys=[expert_id]
    )


class MlopsRun(Base):
    __tablename__ = "mlops_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(40), default="queued")
    epoch: Mapped[int] = mapped_column(Integer, default=0)
    total_epochs: Mapped[int] = mapped_column(Integer, default=20)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
