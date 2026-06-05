"""add user role

Revision ID: c1a2b3d4e5f6
Revises: af66781aeaf9
Create Date: 2026-06-05 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c1a2b3d4e5f6"  # pragma: allowlist secret
down_revision: str | Sequence[str] | None = "af66781aeaf9"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE userrole AS ENUM ('user', 'admin', 'superadmin');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("user", "admin", "superadmin", name="userrole"),
            nullable=False,
            server_default="user",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "role")
    op.execute("DROP TYPE userrole")
