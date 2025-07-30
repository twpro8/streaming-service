"""fix: video_url type

Revision ID: e05d859acc8c
Revises: b83ff96b2e9e
Create Date: 2025-07-30 23:50:44.702238

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e05d859acc8c"
down_revision: Union[str, None] = "b83ff96b2e9e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "episodes",
        "video_url",
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "episodes",
        "video_url",
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        existing_nullable=True,
    )
