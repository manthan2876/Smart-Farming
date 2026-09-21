"""Add feedback review fields.

Revision ID: 0001_feedback_review
Revises:
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0001_feedback_review"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing = {column["name"] for column in inspector.get_columns("feedback")}

    if "review_status" not in existing:
        op.add_column("feedback", sa.Column("review_status", sa.String(length=30), nullable=False, server_default="pending"))
    if "review_decision" not in existing:
        op.add_column("feedback", sa.Column("review_decision", sa.String(length=30), nullable=True))
    if "reviewer_id" not in existing:
        op.add_column("feedback", sa.Column("reviewer_id", sa.String(length=128), nullable=True))
    if "reviewer_note" not in existing:
        op.add_column("feedback", sa.Column("reviewer_note", sa.Text(), nullable=True))
    if "reviewed_at" not in existing:
        op.add_column("feedback", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))

    indexes = {index["name"] for index in inspector.get_indexes("feedback")}
    if "ix_feedback_review_status" not in indexes:
        op.create_index("ix_feedback_review_status", "feedback", ["review_status"])
    if "ix_feedback_reviewer_id" not in indexes:
        op.create_index("ix_feedback_reviewer_id", "feedback", ["reviewer_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("feedback")}
    if "ix_feedback_reviewer_id" in indexes:
        op.drop_index("ix_feedback_reviewer_id", table_name="feedback")
    if "ix_feedback_review_status" in indexes:
        op.drop_index("ix_feedback_review_status", table_name="feedback")

    existing = {column["name"] for column in inspector.get_columns("feedback")}
    for column in ("reviewed_at", "reviewer_note", "reviewer_id", "review_decision", "review_status"):
        if column in existing:
            op.drop_column("feedback", column)
