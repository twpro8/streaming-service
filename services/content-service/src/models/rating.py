# ruff: noqa

from datetime import datetime
from decimal import Decimal

from sqlalchemy import UniqueConstraint, DateTime, text, DECIMAL, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.schemas.pydantic_types import ContentType


class RatingORM(Base):
    __tablename__ = "ratings"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    content_id: Mapped[int]
    content_type: Mapped[ContentType] = mapped_column(String(10))
    rating: Mapped[Decimal] = mapped_column(
        DECIMAL(3, 1), CheckConstraint("rating >= 0 AND rating <= 10")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("TIMEZONE('UTC', now())")
    )

    __table_args__ = (UniqueConstraint("user_id", "content_id", "content_type"),)
