"""create ingredients and steps tables

Revision ID: f4d5e6f7a1b2
Revises: e3c4d5f6a1b2
Create Date: 2026-06-05 13:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from alembic import op

revision: str = "f4d5e6f7a1b2"  # pragma: allowlist secret
down_revision: str | Sequence[str] | None = "e3c4d5f6a1b2"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UNIT_ENUM = ("g", "kg", "ml", "l", "tsp", "tbsp", "pcs", "cup", "pinch", "to_taste")


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ingredients",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_ingredients_name"), "ingredients", ["name"], unique=True)

    values = ", ".join(f"'{v}'" for v in UNIT_ENUM)
    op.execute(sa.text(f"""
        DO $$ BEGIN
            CREATE TYPE ingredientunit AS ENUM ({values});
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """))

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("recipe_id", sa.UUID(), nullable=False),
        sa.Column("ingredient_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "unit",
            PgEnum(*UNIT_ENUM, name="ingredientunit", create_type=False),
            nullable=True,
        ),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recipe_ingredients_recipe_id"),
        "recipe_ingredients",
        ["recipe_id"],
        unique=False,
    )

    op.create_table(
        "recipe_steps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("recipe_id", sa.UUID(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recipe_steps_recipe_id"),
        "recipe_steps",
        ["recipe_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_recipe_steps_recipe_id"), table_name="recipe_steps")
    op.drop_table("recipe_steps")
    op.drop_index(
        op.f("ix_recipe_ingredients_recipe_id"), table_name="recipe_ingredients"
    )
    op.drop_table("recipe_ingredients")
    op.execute("DROP TYPE ingredientunit")
    op.drop_index(op.f("ix_ingredients_name"), table_name="ingredients")
    op.drop_table("ingredients")
