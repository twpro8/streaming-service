"""Update users table

Revision ID: 9b21fafe6a50
Revises: ebf54b8fd0aa
Create Date: 2025-03-30 02:15:10.067514

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b21fafe6a50"
down_revision: Union[str, None] = "ebf54b8fd0aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("provider_id", sa.String(length=255), nullable=True)
    )
    op.alter_column(
        "users", "email", existing_type=sa.VARCHAR(length=255), nullable=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users", "email", existing_type=sa.VARCHAR(length=255), nullable=False
    )
    op.drop_column("users", "provider_id")
