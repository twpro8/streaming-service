"""Add unique constraints to films table / fix: datetime=>date

Revision ID: b41015f2194f
Revises: dd31543bc325
Create Date: 2025-04-18 02:29:14.043524

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b41015f2194f"
down_revision: Union[str, None] = "dd31543bc325"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "films",
        "release_year",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.Date(),
        existing_nullable=False,
    )
    op.create_unique_constraint(None, "films", ["file_id"])
    op.create_unique_constraint(None, "films", ["cover_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "films", type_="unique")
    op.drop_constraint(None, "films", type_="unique")
    op.alter_column(
        "films",
        "release_year",
        existing_type=sa.Date(),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
