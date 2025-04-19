# ruff: noqa

from typing import List

from datetime import date

from sqlalchemy import String, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class FilmORM(Base):
    __tablename__ = "films"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(512))
    director: Mapped[str] = mapped_column(String(255))
    release_year: Mapped[date]
    rating: Mapped[float] = mapped_column(DECIMAL(3, 1))
    duration: Mapped[int]
    file_id: Mapped[int | None] = mapped_column(unique=True)
    cover_id: Mapped[int | None] = mapped_column(unique=True)

    # Relationships
    comments: Mapped[List["CommentORM"]] = relationship(back_populates="film")
