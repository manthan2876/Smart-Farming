"""Baseline migration for core application tables.

Revision ID: 0000_baseline
Revises:
"""

from __future__ import annotations

import sys
from pathlib import Path
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# Ensure backend src is in sys.path
backend_src = Path(__file__).resolve().parents[2] / "src"
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

from app.core import Base
import app.models

revision = "0000_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # Create tables defined in Base.metadata that do not yet exist,
    # excluding tables managed by later migrations (password_reset_tokens in 0002).
    for table in Base.metadata.sorted_tables:
        if table.name == "password_reset_tokens":
            continue
        if table.name not in existing_tables:
            table.create(bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table in reversed(Base.metadata.sorted_tables):
        if table.name == "password_reset_tokens":
            continue
        if table.name in existing_tables:
            table.drop(bind, checkfirst=True)

