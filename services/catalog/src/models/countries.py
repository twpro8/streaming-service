from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, int_pk, str_2, str_64


class CountryORM(Base):
    """
    code: ISO 3166-1 alpha-2 (example: "US")
    name: full country name in English
    """

    __tablename__ = "countries"

    id: Mapped[int_pk]
    code: Mapped[str_2] = mapped_column(unique=True, index=True)
    name: Mapped[str_64] = mapped_column(unique=True)

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
