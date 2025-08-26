from typing import List

from sqlalchemy import String
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
