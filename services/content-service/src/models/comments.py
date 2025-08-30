from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base


class CommentORM(Base):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True))
    content_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True))
    content_type: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )  # Make sure you have added the trigger to the migration.
