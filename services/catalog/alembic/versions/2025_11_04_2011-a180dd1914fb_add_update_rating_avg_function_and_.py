"""add update_rating_avg function and trigger

Revision ID: a180dd1914fb
Revises: 97965ac8b4fd
Create Date: 2025-11-04 20:11:41.173185

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a180dd1914fb"
down_revision: Union[str, None] = "97965ac8b4fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text("""
    CREATE OR REPLACE FUNCTION update_rating_avg()
    RETURNS trigger AS $$
    BEGIN
        NEW.rating_avg := ROUND(NEW.rating_sum / NULLIF(NEW.rating_count, 0), 1);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """))
    op.execute(sa.text("""
    CREATE TRIGGER trg_update_rating_avg
    BEFORE INSERT OR UPDATE ON rating_aggregates
    FOR EACH ROW
    EXECUTE FUNCTION update_rating_avg();
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS trg_update_rating_avg ON rating_aggregates;")
    op.execute("DROP FUNCTION IF EXISTS update_rating_avg();")
