"""add unique constrains for urls

Revision ID: b83ff96b2e9e
Revises: 7bd1bc433bcb
Create Date: 2025-07-18 09:52:03.728003

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b83ff96b2e9e"
down_revision: Union[str, None] = "7bd1bc433bcb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(None, "episodes", ["video_url"])
    op.create_unique_constraint(None, "films", ["cover_url"])
    op.create_unique_constraint(None, "films", ["video_url"])
    op.create_unique_constraint(None, "series", ["cover_url"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "series", type_="unique")
    op.drop_constraint(None, "films", type_="unique")
    op.drop_constraint(None, "films", type_="unique")
    op.drop_constraint(None, "episodes", type_="unique")
