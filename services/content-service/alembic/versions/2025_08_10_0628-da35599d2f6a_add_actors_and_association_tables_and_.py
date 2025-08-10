"""add actors and association tables and add trigger

Revision ID: da35599d2f6a
Revises: 03f11fb07a2d
Create Date: 2025-08-10 06:28:55.725312

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "da35599d2f6a"
down_revision: Union[str, None] = "03f11fb07a2d"
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
                "ARIES",
                "TAURUS",
                "GEMINI",
                "CANCER",
                "LEO",
                "VIRGO",
                "LIBRA",
                "SCORPIO",
                "SAGITTARIUS",
                "CAPRICORN",
                "AQUARIUS",
                "PISCES",
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
        "film_actor_associations",
        sa.Column("film_id", sa.UUID(), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_id"], ["actors.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["film_id"], ["films.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("film_id", "actor_id"),
    )
    op.create_table(
        "series_actor_associations",
        sa.Column("series_id", sa.UUID(), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_id"], ["actors.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["series_id"], ["series.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("series_id", "actor_id"),
    )

    # Creating function for updating updated_at column
    op.execute(text("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
      NEW.updated_at = NOW() AT TIME ZONE 'UTC';
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """))

    # Creating trigger
    op.execute(text("""
    CREATE TRIGGER update_actors_updated_at
    BEFORE UPDATE ON actors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS update_actors_updated_at ON actors;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    op.drop_table("series_actor_associations")
    op.drop_table("film_actor_associations")
    op.drop_table("actors")
