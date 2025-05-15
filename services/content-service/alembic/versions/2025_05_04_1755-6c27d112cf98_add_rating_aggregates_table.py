"""add rating_aggregates table

Revision ID: 6c27d112cf98
Revises: a5dcb6c5d276
Create Date: 2025-05-04 17:55:39.904946

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6c27d112cf98"
down_revision: Union[str, None] = "a5dcb6c5d276"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "rating_aggregates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(length=10), nullable=False),
        sa.Column("rating_sum", sa.DECIMAL(precision=10, scale=1), nullable=False),
        sa.Column("rating_count", sa.Integer(), nullable=False),
        sa.Column("rating_avg", sa.DECIMAL(precision=3, scale=1), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_id", "content_type"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("rating_aggregates")
