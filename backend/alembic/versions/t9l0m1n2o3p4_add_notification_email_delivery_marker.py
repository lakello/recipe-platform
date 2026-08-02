"""add notification email delivery marker

Revision ID: t9l0m1n2o3p4
Revises: s8k9l0m1n2o3
Create Date: 2026-08-02 18:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "t9l0m1n2o3p4"
down_revision: str | Sequence[str] | None = "s8k9l0m1n2o3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "notifications",
        sa.Column("email_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("notifications", "email_sent_at")
