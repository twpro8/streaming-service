"""create all tables

Revision ID: d9df3ac95dd8
Revises:
Create Date: 2025-08-25 17:34:37.094939

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d9df3ac95dd8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "actors",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(length=48), nullable=False),
        sa.Column("last_name", sa.String(length=48), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column(
            "zodiac_sign",
            sa.Enum(
                "aries",
                "taurus",
                "gemini",
                "cancer",
                "leo",
                "virgo",
                "libra",
                "scorpio",
                "sagittarius",
                "capricorn",
                "aquarius",
                "pisces",
                name="zodiacsign",
            ),
            nullable=True,
        ),
        sa.Column("bio", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "first_name",
            "last_name",
            "birth_date",
            name="unique_actors_full_identity",
        ),
    )
    op.create_table(
        "genres",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "movies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("director", sa.String(length=255), nullable=False),
        sa.Column("release_year", sa.Date(), nullable=False),
        sa.Column("rating", sa.DECIMAL(precision=3, scale=1), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("video_url", sa.String(), nullable=True),
        sa.Column("cover_url", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cover_url"),
        sa.UniqueConstraint("video_url"),
    )
    op.create_table(
        "rating_aggregates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column(
            "rating_sum", sa.DECIMAL(precision=10, scale=1), nullable=False
        ),
        sa.Column("rating_count", sa.Integer(), nullable=False),
        sa.Column(
            "rating_avg", sa.DECIMAL(precision=3, scale=1), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ratings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column("value", sa.DECIMAL(precision=3, scale=1), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.CheckConstraint("value >= 0 AND value <= 10"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "content_id"),
    )
    op.create_table(
        "shows",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("director", sa.String(length=255), nullable=False),
        sa.Column("release_year", sa.Date(), nullable=False),
        sa.Column("rating", sa.DECIMAL(precision=3, scale=1), nullable=False),
        sa.Column("cover_url", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cover_url"),
    )
    op.create_table(
        "comments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("movie_id", sa.UUID(), nullable=True),
        sa.Column("show_id", sa.UUID(), nullable=True),
        sa.Column("comment", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["movie_id"], ["movies.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["show_id"], ["shows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "movie_actor_associations",
        sa.Column("movie_id", sa.UUID(), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_id"], ["actors.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["movie_id"], ["movies.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("movie_id", "actor_id"),
    )
    op.create_table(
        "movie_genre_associations",
        sa.Column("movie_id", sa.UUID(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["genre_id"], ["genres.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["movie_id"], ["movies.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("movie_id", "genre_id"),
    )
    op.create_table(
        "seasons",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("show_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("season_number", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["show_id"], ["shows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "show_id", "season_number", name="unique_season_per_show"
        ),
    )
    op.create_table(
        "show_actor_associations",
        sa.Column("show_id", sa.UUID(), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_id"], ["actors.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["show_id"], ["shows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("show_id", "actor_id"),
    )
    op.create_table(
        "show_genre_associations",
        sa.Column("show_id", sa.UUID(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["genre_id"], ["genres.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["show_id"], ["shows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("show_id", "genre_id"),
    )
    op.create_table(
        "episodes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("show_id", sa.UUID(), nullable=False),
        sa.Column("season_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("episode_number", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("video_url", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["season_id"], ["seasons.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["show_id"], ["shows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "season_id", "episode_number", name="unique_episode_per_season"
        ),
        sa.UniqueConstraint("video_url"),
    )
    op.execute(sa.text("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
      NEW.updated_at = NOW() AT TIME ZONE 'UTC';
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """))
    op.execute(sa.text("""
    CREATE TRIGGER update_actors_updated_at
    BEFORE UPDATE ON actors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS update_actors_updated_at ON actors;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    op.drop_table("episodes")
    op.drop_table("show_genre_associations")
    op.drop_table("show_actor_associations")
    op.drop_table("seasons")
    op.drop_table("movie_genre_associations")
    op.drop_table("movie_actor_associations")
    op.drop_table("comments")
    op.drop_table("shows")
    op.drop_table("ratings")
    op.drop_table("rating_aggregates")
    op.drop_table("movies")
    op.drop_table("genres")
    op.drop_table("actors")
    op.execute("DROP TYPE IF EXISTS zodiacsign;")
