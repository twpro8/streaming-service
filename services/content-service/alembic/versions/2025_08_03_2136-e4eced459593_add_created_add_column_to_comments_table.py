"""add created_add column to comments table

Revision ID: e4eced459593
Revises: e05d859acc8c
Create Date: 2025-08-03 21:36:11.722133

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4eced459593"
down_revision: Union[str, None] = "e05d859acc8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "comments", sa.Column("comment", sa.String(length=255), nullable=False)
    )
    op.add_column(
        "comments",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
    )
    op.drop_column("comments", "text")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "comments",
        sa.Column(
            "text", sa.VARCHAR(length=255), autoincrement=False, nullable=False
        ),
    )
    op.drop_column("comments", "created_at")
    op.drop_column("comments", "comment")
