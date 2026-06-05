"""add avatar_url to users and create recipe_photos table

Revision ID: a1b2c3d4e5f7
Revises: f4d5e6f7a1b2
Create Date: 2026-06-05 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1b2c3d4e5f7"  # pragma: allowlist secret
down_revision: str | Sequence[str] | None = "f4d5e6f7a1b2"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("avatar_url", sa.String(length=512), nullable=True))

    op.create_table(
        "recipe_photos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("recipe_id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recipe_id"),
    )
    op.create_index(
        op.f("ix_recipe_photos_recipe_id"), "recipe_photos", ["recipe_id"], unique=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_recipe_photos_recipe_id"), table_name="recipe_photos")
    op.drop_table("recipe_photos")
    op.drop_column("users", "avatar_url")
