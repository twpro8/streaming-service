# ruff: noqa

from typing import List
from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class GenreORM(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    # Relationships
    films: Mapped[List["FilmORM"]] = relationship(
        secondary="film_genre_associations",
        back_populates="genres",
    )
    series: Mapped[List["SeriesORM"]] = relationship(
        secondary="series_genre_associations",
        back_populates="genres",
    )

    def __repr__(self):
        return f"<GenreORM(id={self.id}, title='{self.name}')>"

    def __str__(self):
        return f"{self.name}"


class FilmGenreORM(Base):
    __tablename__ = "film_genre_associations"

    film_id: Mapped[UUID] = mapped_column(
        ForeignKey("films.id", ondelete="CASCADE"), primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True
    )


class SeriesGenreORM(Base):
    __tablename__ = "series_genre_associations"

    series_id: Mapped[UUID] = mapped_column(
        ForeignKey("series.id", ondelete="CASCADE"), primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True
    )
