"""Add uq_user_client constraint to refresh_tokens table

Revision ID: 5fc9a133585f
Revises: e82807b3ac34
Create Date: 2025-10-19 09:54:56.932512

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5fc9a133585f"
down_revision: Union[str, None] = "e82807b3ac34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_user_client", "refresh_tokens", ["user_id", "ip", "user_agent"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_user_client", "refresh_tokens", type_="unique")
