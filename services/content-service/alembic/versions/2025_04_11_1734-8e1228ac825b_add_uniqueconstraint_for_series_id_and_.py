"""Add UniqueConstraint for series_id and season_number

Revision ID: 8e1228ac825b
Revises: 4baeec0028cf
Create Date: 2025-04-11 17:34:11.466180

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8e1228ac825b"
down_revision: Union[str, None] = "4baeec0028cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("unique_season", "seasons", ["series_id", "season_number"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("unique_season", "seasons", type_="unique")
