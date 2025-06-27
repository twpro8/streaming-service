"""Create all tables

Revision ID: 23eb614179ca
Revises:
Create Date: 2025-05-23 20:21:30.583417

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "23eb614179ca"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "films",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("director", sa.String(length=255), nullable=False),
        sa.Column("release_year", sa.Date(), nullable=False),
        sa.Column("rating", sa.DECIMAL(precision=3, scale=1), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=True),
        sa.Column("cover_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cover_id"),
        sa.UniqueConstraint("file_id"),
    )
    op.create_table(
        "rating_aggregates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column("rating_sum", sa.DECIMAL(precision=10, scale=1), nullable=False),
        sa.Column("rating_count", sa.Integer(), nullable=False),
        sa.Column("rating_avg", sa.DECIMAL(precision=3, scale=1), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ratings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column("rating", sa.DECIMAL(precision=3, scale=1), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "content_id"),
    )
    op.create_table(
        "series",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("director", sa.String(length=255), nullable=False),
        sa.Column("release_year", sa.Date(), nullable=False),
        sa.Column("rating", sa.DECIMAL(precision=3, scale=1), nullable=False),
        sa.Column("cover_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "comments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("film_id", sa.UUID(), nullable=True),
        sa.Column("series_id", sa.UUID(), nullable=True),
        sa.Column("text", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["film_id"], ["films.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["series_id"], ["series.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "seasons",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("series_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("season_number", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["series_id"], ["series.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("series_id", "season_number", name="unique_season_per_series"),
    )
    op.create_table(
        "episodes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("series_id", sa.UUID(), nullable=False),
        sa.Column("season_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("episode_number", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["season_id"],
            ["seasons.id"],
        ),
        sa.ForeignKeyConstraint(["series_id"], ["series.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_id"),
        sa.UniqueConstraint("season_id", "episode_number", name="unique_episode_per_season"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("episodes")
    op.drop_table("seasons")
    op.drop_table("comments")
    op.drop_table("series")
    op.drop_table("ratings")
    op.drop_table("rating_aggregates")
    op.drop_table("films")
