"""Add genre orm and association tables

Revision ID: 03f11fb07a2d
Revises: 705db6d50cf9
Create Date: 2025-08-08 23:15:14.836205

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "03f11fb07a2d"
down_revision: Union[str, None] = "705db6d50cf9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "genres",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "film_genre_associations",
        sa.Column("film_id", sa.UUID(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["film_id"], ["films.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["genre_id"], ["genres.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("film_id", "genre_id"),
    )
    op.create_table(
        "series_genre_associations",
        sa.Column("series_id", sa.UUID(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["genre_id"], ["genres.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["series_id"], ["series.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("series_id", "genre_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("series_genre_associations")
    op.drop_table("film_genre_associations")
    op.drop_table("genres")
