from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class CountryORM(Base):
    """
    code: ISO 3166-1 alpha-2 (example: "US")
    name: full country name in English
    """

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relationships
    movies: Mapped[List["MovieORM"]] = relationship(
        secondary="movie_country_associations",
        back_populates="countries",
    )
    shows: Mapped[List["ShowORM"]] = relationship(
        secondary="show_country_associations",
        back_populates="countries",
    )

    def __repr__(self):
        return f"<CountryORM(id={self.id!r}, code={self.code!r}, name={self.name!r})>"
