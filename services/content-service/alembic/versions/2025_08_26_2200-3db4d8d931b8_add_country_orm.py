"""add country orm

Revision ID: 3db4d8d931b8
Revises: 22b9294f5d51
Create Date: 2025-08-26 22:00:57.307600

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3db4d8d931b8"
down_revision: Union[str, None] = "22b9294f5d51"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=2), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_countries_code"), "countries", ["code"], unique=True
    )
    op.create_table(
        "movie_country_associations",
        sa.Column("movie_id", sa.UUID(), nullable=False),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["country_id"], ["countries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["movie_id"], ["movies.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("movie_id", "country_id"),
    )
    op.create_table(
        "show_country_associations",
        sa.Column("show_id", sa.UUID(), nullable=False),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["country_id"], ["countries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["show_id"], ["shows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("show_id", "country_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("show_country_associations")
    op.drop_table("movie_country_associations")
    op.drop_index(op.f("ix_countries_code"), table_name="countries")
    op.drop_table("countries")
