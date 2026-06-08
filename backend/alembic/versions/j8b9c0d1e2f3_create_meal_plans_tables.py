"""create meal_plans tables

Revision ID: j8b9c0d1e2f3
Revises: i7a8b9c0d1e2
Create Date: 2026-06-08 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "j8b9c0d1e2f3"
down_revision: str | None = "i7a8b9c0d1e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MEAL_TYPE_ENUM = ("breakfast", "lunch", "dinner", "snack")


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        sa.text(
            "DO $$ BEGIN "
            "CREATE TYPE mealtype AS ENUM ('breakfast','lunch','dinner','snack'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; "
            "END $$;"
        )
    )

    op.create_table(
        "meal_plans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "week_start", name="uq_meal_plan_user_week"),
    )
    op.create_index("ix_meal_plans_user_id", "meal_plans", ["user_id"])

    op.create_table(
        "meal_plan_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("meal_plan_id", sa.UUID(), nullable=False),
        sa.Column("recipe_id", sa.UUID(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column(
            "meal_type",
            sa.Enum(*MEAL_TYPE_ENUM, name="mealtype", create_type=False),
            nullable=False,
        ),
        sa.Column("servings", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["meal_plan_id"], ["meal_plans.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_meal_plan_items_meal_plan_id", "meal_plan_items", ["meal_plan_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("meal_plan_items")
    op.drop_table("meal_plans")
    op.execute(sa.text("DROP TYPE IF EXISTS mealtype;"))
