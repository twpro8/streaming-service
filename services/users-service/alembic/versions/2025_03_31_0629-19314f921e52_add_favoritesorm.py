"""Add FavoritesORM

Revision ID: 19314f921e52
Revises: 9b21fafe6a50
Create Date: 2025-03-31 06:29:31.336926

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "19314f921e52"
down_revision: Union[str, None] = "9b21fafe6a50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("film_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "film_id", name="uq_user_film"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("favorites")
