"""add videos and images tables

Revision ID: 21f7cbe68f80
Revises:
Create Date: 2025-06-29 18:21:22.096176

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "21f7cbe68f80"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "images",
        sa.Column("content_id", sa.UUID(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=False),
        sa.Column("size_in_bytes", sa.BigInteger(), nullable=False),
        sa.Column(
            "content_type",
            sa.Enum("film", "series", name="content_type_enum"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("content_id"),
    )
    op.create_table(
        "videos",
        sa.Column("content_id", sa.UUID(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=False),
        sa.Column("size_in_bytes", sa.BigInteger(), nullable=False),
        sa.Column(
            "content_type",
            sa.Enum("film", "series", name="content_type_enum"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("content_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("videos")
    op.drop_table("images")
