"""add language orm

Revision ID: 8b96e3041478
Revises: 3db4d8d931b8
Create Date: 2025-08-26 22:06:55.335620

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8b96e3041478"
down_revision: Union[str, None] = "3db4d8d931b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "languages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=2), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_languages_code"), "languages", ["code"], unique=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_languages_code"), table_name="languages")
    op.drop_table("languages")
