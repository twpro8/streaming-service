"""unique_episode_per_season

Revision ID: dd31543bc325
Revises: 8e1228ac825b
Create Date: 2025-04-18 01:57:12.826236

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dd31543bc325"
down_revision: Union[str, None] = "8e1228ac825b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "unique_episode_per_season",
        "episodes",
        ["season_id", "episode_number"],
    )
    op.create_unique_constraint(None, "episodes", ["file_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "episodes", type_="unique")
    op.drop_constraint("unique_episode_per_season", "episodes", type_="unique")
