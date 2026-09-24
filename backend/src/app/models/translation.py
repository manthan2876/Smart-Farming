from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core import Base


class EntityTranslation(Base):
    __tablename__ = "entity_translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)   # 'recommendation', 'expert_review', 'alert', 'farm', 'plot'
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)    # ID as string
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)                # 'title', 'body', 'fertilizer', 'farmer_guidance', etc.
    language: Mapped[str] = mapped_column(String(10), nullable=False)                  # 'gu', 'hi'
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False)               # SHA256 of the English source
    is_transliteration: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="done")                     # 'pending', 'done', 'failed'
    retries: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", "field_name", "language", name="uq_entity_translation_field"),
        Index("ix_entity_lookup", "entity_type", "entity_id", "language"),
    )
