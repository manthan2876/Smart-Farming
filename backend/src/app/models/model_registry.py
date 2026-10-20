from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core import Base


class ModelRegistryRecord(Base):
    __tablename__ = "model_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_key: Mapped[str] = mapped_column(String(100), index=True)
    version: Mapped[str] = mapped_column(String(50))
    arch: Mapped[str] = mapped_column(String(100))
    hf_repo_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    hf_weight_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    checkpoint_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    labels_json: Mapped[list[str]] = mapped_column(JSON)
    num_classes: Mapped[int] = mapped_column(Integer)
    val_acc: Mapped[float] = mapped_column(Float)
    test_acc: Mapped[float] = mapped_column(Float)
    macro_f1: Mapped[float | None] = mapped_column(Float, nullable=True)
    per_class_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[str] = mapped_column(String(50), default="active")
    dataset_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    git_commit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    random_seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    promoted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    promoted_by: Mapped[str] = mapped_column(String(100))

