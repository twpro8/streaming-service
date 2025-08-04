"""changle column name from rating to value for RatingORM

Revision ID: 705db6d50cf9
Revises: e4eced459593
Create Date: 2025-08-04 17:47:02.670392

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "705db6d50cf9"
down_revision: Union[str, None] = "e4eced459593"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "ratings",
        sa.Column("value", sa.DECIMAL(precision=3, scale=1), nullable=False),
    )
    op.drop_column("ratings", "rating")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "ratings",
        sa.Column(
            "rating",
            sa.NUMERIC(precision=3, scale=1),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("ratings", "value")
