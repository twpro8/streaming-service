from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base, uuid_pk, str_256, created_at


class RefreshTokenORM(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    token_hash: Mapped[str_256]
    created_at: Mapped[created_at]
    updated_at: Mapped[created_at]  # Make sure you have added the trigger to the migration.
