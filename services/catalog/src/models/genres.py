from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, int_pk, str_64


class GenreORM(Base):
    __tablename__ = "genres"

    id: Mapped[int_pk]
    name: Mapped[str_64] = mapped_column(unique=True)

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
