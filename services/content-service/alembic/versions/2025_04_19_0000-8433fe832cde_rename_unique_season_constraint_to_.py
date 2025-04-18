"""Rename unique_season constraint to unique_season_per_series

Revision ID: 8433fe832cde
Revises: b41015f2194f
Create Date: 2025-04-19 00:00:14.078436

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8433fe832cde"
down_revision: Union[str, None] = "b41015f2194f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("unique_season", "seasons", type_="unique")
    op.create_unique_constraint(
        "unique_season_per_series", "seasons", ["series_id", "season_number"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("unique_season_per_series", "seasons", type_="unique")
    op.create_unique_constraint("unique_season", "seasons", ["series_id", "season_number"])
