"""add rating orm

Revision ID: a5dcb6c5d276
Revises: 8433fe832cde
Create Date: 2025-05-02 15:11:58.000561

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a5dcb6c5d276"
down_revision: Union[str, None] = "8433fe832cde"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(length=10), nullable=False),
        sa.Column("rating", sa.DECIMAL(precision=3, scale=1), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "content_id", "content_type"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("ratings")
