from datetime import datetime

from sqlalchemy import String, BigInteger, DateTime, text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.schemas.pydantic_types import ContentType


class FileORM(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))  # Original filename
    path: Mapped[str] = mapped_column(String(255))  # Full S3 path (e.g. "films/1/first_film.mp4")
    mime_type: Mapped[str] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(BigInteger)
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType, name="content_type_enum"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("TIMEZONE('UTC', now())")
    )
