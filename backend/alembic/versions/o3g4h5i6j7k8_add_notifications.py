"""add notifications

Revision ID: o3g4h5i6j7k8
Revises: n2f3a4b5c6d7
Create Date: 2026-06-09 01:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "o3g4h5i6j7k8"
down_revision: str | None = "n2f3a4b5c6d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

notification_type = postgresql.ENUM(
    "like", "comment", "reply", "follow", "moderation",
    name="notificationtype",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "CREATE TYPE IF NOT EXISTS notificationtype AS ENUM "
        "('like', 'comment', 'reply', 'follow', 'moderation')"
    )
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "actor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("entity_type", sa.String(20), nullable=True),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column(
            "is_read",
            sa.Boolean,
            nullable=False,
            server_default="f",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        if_not_exists=True,
    )
    op.create_index(
        "ix_notifications_user_id", "notifications", ["user_id"], if_not_exists=True
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.execute("DROP TYPE notificationtype")
