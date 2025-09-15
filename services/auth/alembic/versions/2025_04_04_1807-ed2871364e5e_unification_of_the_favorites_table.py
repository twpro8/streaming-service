"""Unification of the Favorites Table

Revision ID: ed2871364e5e
Revises: 1722ded271fc
Create Date: 2025-04-04 18:07:35.616104

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ed2871364e5e"
down_revision: Union[str, None] = "1722ded271fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("favorites", sa.Column("content_id", sa.Integer(), nullable=False))
    op.add_column("favorites", sa.Column("content_type", sa.String(), nullable=False))
    op.drop_constraint("uq_user_film", "favorites", type_="unique")
    op.create_unique_constraint(
        "unique_favorite",
        "favorites",
        ["user_id", "content_id", "content_type"],
    )
    op.drop_column("favorites", "film_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "favorites",
        sa.Column("film_id", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.drop_constraint("unique_favorite", "favorites", type_="unique")
    op.create_unique_constraint("uq_user_film", "favorites", ["user_id", "film_id"])
    op.drop_column("favorites", "content_type")
    op.drop_column("favorites", "content_id")
