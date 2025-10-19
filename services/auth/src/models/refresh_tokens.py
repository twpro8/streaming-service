from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, DateTime, String
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
    ip: Mapped[str] = mapped_column(String(15))
    user_agent: Mapped[str_256]
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[created_at]
