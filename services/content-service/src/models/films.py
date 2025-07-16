# ruff: noqa

from typing import List
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import date

from sqlalchemy import String, DECIMAL, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base


class FilmORM(Base):
    __tablename__ = "films"
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(512))
    director: Mapped[str] = mapped_column(String(255))
    release_year: Mapped[date]
    rating: Mapped[Decimal] = mapped_column(
        DECIMAL(3, 1),
        CheckConstraint("rating >= 0 AND rating <= 10"),
        default=Decimal("0.0"),
    )
    duration: Mapped[int]
    video_url: Mapped[str | None]
    cover_url: Mapped[str | None]

    # Relationships
    comments: Mapped[List["CommentORM"]] = relationship(back_populates="film")
