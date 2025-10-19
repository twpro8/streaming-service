"""add ip and user_agent fields to refresh_tokens table

Revision ID: f423d67c27bb
Revises: dda7bfdd60c4
Create Date: 2025-10-06 01:36:41.578691

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f423d67c27bb"
down_revision: Union[str, None] = "dda7bfdd60c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "refresh_tokens",
        sa.Column("ip", sa.String(length=15), nullable=False),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("user_agent", sa.String(length=256), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("refresh_tokens", "user_agent")
    op.drop_column("refresh_tokens", "ip")
