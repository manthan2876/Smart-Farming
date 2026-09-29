"""Add password reset tokens table.

Revision ID: 0002_password_reset
Revises: 0001_feedback_review
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_password_reset"
down_revision = "0001_feedback_review"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "password_reset_tokens" not in tables:
        op.create_table(
            "password_reset_tokens",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.String(length=128), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
        op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"])
        op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expires_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "password_reset_tokens" in tables:
        op.drop_index("ix_password_reset_tokens_expires_at", table_name="password_reset_tokens")
        op.drop_index("ix_password_reset_tokens_token_hash", table_name="password_reset_tokens")
        op.drop_index("ix_password_reset_tokens_user_id", table_name="password_reset_tokens")
        op.drop_table("password_reset_tokens")
