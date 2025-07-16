"""Change file/cover ids to urls

Revision ID: 7bd1bc433bcb
Revises: 23eb614179ca
Create Date: 2025-07-16 03:21:15.209704

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7bd1bc433bcb"
down_revision: Union[str, None] = "23eb614179ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("episodes", sa.Column("video_url", sa.Integer(), nullable=True))
    op.drop_constraint("episodes_file_id_key", "episodes", type_="unique")
    op.drop_column("episodes", "file_id")
    op.add_column("films", sa.Column("video_url", sa.String(), nullable=True))
    op.add_column("films", sa.Column("cover_url", sa.String(), nullable=True))
    op.drop_constraint("films_cover_id_key", "films", type_="unique")
    op.drop_constraint("films_file_id_key", "films", type_="unique")
    op.drop_column("films", "cover_id")
    op.drop_column("films", "file_id")
    op.add_column("series", sa.Column("cover_url", sa.String(), nullable=True))
    op.drop_column("series", "cover_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "series",
        sa.Column("cover_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.drop_column("series", "cover_url")
    op.add_column(
        "films",
        sa.Column("file_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "films",
        sa.Column("cover_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_unique_constraint("films_file_id_key", "films", ["file_id"])
    op.create_unique_constraint("films_cover_id_key", "films", ["cover_id"])
    op.drop_column("films", "cover_url")
    op.drop_column("films", "video_url")
    op.add_column(
        "episodes",
        sa.Column("file_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_unique_constraint("episodes_file_id_key", "episodes", ["file_id"])
    op.drop_column("episodes", "video_url")
