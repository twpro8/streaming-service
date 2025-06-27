from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import String, BigInteger, DateTime, text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.core.enums import ContentType
from src.db import Base


class FileORM(Base):
    __tablename__ = "files"
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    content_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), index=True)
    filename: Mapped[str] = mapped_column(String(255))  # Original filename
    s3_key: Mapped[str] = mapped_column(String(255))  # Full S3 path
    mime_type: Mapped[str] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(BigInteger)
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType, name="content_type_enum"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("TIMEZONE('UTC', now())")
    )
