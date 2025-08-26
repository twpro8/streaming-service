"""add director orm

Revision ID: 22b9294f5d51
Revises: 93a29d39d13e
Create Date: 2025-08-26 21:14:36.184304

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "22b9294f5d51"
down_revision: Union[str, None] = "93a29d39d13e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "directors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=48), nullable=False),
        sa.Column("last_name", sa.String(length=48), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column(
            "zodiac_sign",
            postgresql.ENUM(name="zodiacsign", create_type=False),
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
            name="unique_directors_full_identity",
        ),
    )
    op.create_table(
        "movie_director_associations",
        sa.Column("movie_id", sa.UUID(), nullable=False),
        sa.Column("director_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["director_id"], ["directors.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["movie_id"], ["movies.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("movie_id", "director_id"),
    )
    op.create_table(
        "show_director_associations",
        sa.Column("show_id", sa.UUID(), nullable=False),
        sa.Column("director_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["director_id"], ["directors.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["show_id"], ["shows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("show_id", "director_id"),
    )
    op.drop_column("movies", "director")
    op.drop_column("shows", "director")
    op.execute(sa.text("""
    CREATE TRIGGER update_directors_updated_at
    BEFORE UPDATE ON directors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS update_directors_updated_at ON directors;")
    op.add_column(
        "movies",
        sa.Column(
            "director",
            sa.VARCHAR(length=255),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "shows",
        sa.Column(
            "director",
            sa.VARCHAR(length=255),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_table("movie_director_associations")
    op.drop_table("show_director_associations")
    op.drop_table("directors")
