"""refresh_tokens table: delete token_hash and updated_at, add expires_at

Revision ID: e82807b3ac34
Revises: f423d67c27bb
Create Date: 2025-10-18 08:32:48.295656

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e82807b3ac34"
down_revision: Union[str, None] = "f423d67c27bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "refresh_tokens",
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.drop_column("refresh_tokens", "updated_at")
    op.drop_column("refresh_tokens", "token_hash")
    op.execute("DROP TRIGGER IF EXISTS update_refresh_tokens_updated_at ON refresh_tokens;")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "token_hash",
            sa.VARCHAR(length=256),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('UTC'::text, now())"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("refresh_tokens", "expires_at")
    op.execute(sa.text("""
        CREATE TRIGGER update_refresh_tokens_updated_at
        BEFORE UPDATE ON refresh_tokens
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
        """))
