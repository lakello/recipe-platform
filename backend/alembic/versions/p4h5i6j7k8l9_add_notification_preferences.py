"""add notification preferences

Revision ID: p4h5i6j7k8l9
Revises: o3g4h5i6j7k8
Create Date: 2026-06-09 02:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "p4h5i6j7k8l9"
down_revision: str | None = "o3g4h5i6j7k8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notification_preferences",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "email_like", sa.Boolean, nullable=False, server_default="t"
        ),
        sa.Column(
            "email_comment", sa.Boolean, nullable=False, server_default="t"
        ),
        sa.Column(
            "email_follow", sa.Boolean, nullable=False, server_default="t"
        ),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("notification_preferences")
