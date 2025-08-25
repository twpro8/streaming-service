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
    movies: Mapped[List["MovieORM"]] = relationship(
        secondary="movie_genre_associations",
        back_populates="genres",
    )
    shows: Mapped[List["ShowORM"]] = relationship(
        secondary="show_genre_associations",
        back_populates="genres",
    )

    def __repr__(self):
        return f"<GenreORM(id={self.id}, title='{self.name}')>"

    def __str__(self):
        return f"{self.name}"


class MovieGenreORM(Base):
    __tablename__ = "movie_genre_associations"

    movie_id: Mapped[UUID] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ShowGenreORM(Base):
    __tablename__ = "show_genre_associations"

    show_id: Mapped[UUID] = mapped_column(
        ForeignKey("shows.id", ondelete="CASCADE"),
        primary_key=True,
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    )
