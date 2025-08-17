"""on delete cascade for season orm

Revision ID: 5f498c432fc5
Revises: da35599d2f6a
Create Date: 2025-08-15 11:31:10.883490

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5f498c432fc5"
down_revision: Union[str, None] = "da35599d2f6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "episodes_season_id_fkey", "episodes", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "episodes", "seasons", ["season_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "episodes", type_="foreignkey")
    op.create_foreign_key(
        "episodes_season_id_fkey", "episodes", "seasons", ["season_id"], ["id"]
    )
