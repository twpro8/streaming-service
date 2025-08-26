"""add created_at and updated_at fields

Revision ID: 93a29d39d13e
Revises: d9df3ac95dd8
Create Date: 2025-08-25 19:28:27.110968

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "93a29d39d13e"
down_revision: Union[str, None] = "d9df3ac95dd8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "comments",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )
    op.add_column(
        "episodes",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )
    op.add_column(
        "episodes",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )
    op.add_column(
        "movies",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )
    op.add_column(
        "movies",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )
    op.drop_column("ratings", "created_at")
    op.add_column(
        "seasons",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )
    op.add_column(
        "seasons",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )
    op.add_column(
        "shows",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )
    op.add_column(
        "shows",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )
    op.alter_column(
        "comments",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("timezone('UTC'::text, now())"),
    )
    op.execute(sa.text("""
    CREATE TRIGGER update_comments_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """))
    op.execute(sa.text("""
    CREATE TRIGGER update_episodes_updated_at
    BEFORE UPDATE ON episodes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """))
    op.execute(sa.text("""
    CREATE TRIGGER update_movies_updated_at
    BEFORE UPDATE ON movies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """))
    op.execute(sa.text("""
    CREATE TRIGGER update_seasons_updated_at
    BEFORE UPDATE ON seasons
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """))
    op.execute(sa.text("""
    CREATE TRIGGER update_shows_updated_at
    BEFORE UPDATE ON shows
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS update_comments_updated_at ON comments;")
    op.execute("DROP TRIGGER IF EXISTS update_episodes_updated_at ON episodes;")
    op.execute("DROP TRIGGER IF EXISTS update_movies_updated_at ON movies;")
    op.execute("DROP TRIGGER IF EXISTS update_seasons_updated_at ON seasons;")
    op.execute("DROP TRIGGER IF EXISTS update_shows_updated_at ON shows;")
    op.alter_column(
        "comments",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        existing_server_default=sa.text("timezone('UTC'::text, now())"),
    )
    op.drop_column("shows", "updated_at")
    op.drop_column("shows", "created_at")
    op.drop_column("seasons", "updated_at")
    op.drop_column("seasons", "created_at")
    op.add_column(
        "ratings",
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("timezone('UTC'::text, now())"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("movies", "updated_at")
    op.drop_column("movies", "created_at")
    op.drop_column("episodes", "updated_at")
    op.drop_column("episodes", "created_at")
    op.drop_column("comments", "updated_at")
