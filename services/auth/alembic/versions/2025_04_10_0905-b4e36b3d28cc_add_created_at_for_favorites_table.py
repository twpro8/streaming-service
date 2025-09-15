"""Add created_at for favorites table

Revision ID: b4e36b3d28cc
Revises: ed2871364e5e
Create Date: 2025-04-10 09:05:13.421954

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b4e36b3d28cc"
down_revision: Union[str, None] = "ed2871364e5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "favorites",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("favorites", "created_at")
