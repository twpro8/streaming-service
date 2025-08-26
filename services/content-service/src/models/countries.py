from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class CountryORM(Base):
    """
    alpha2: ISO 3166-1 alpha-2 (example: "US")
    alpha3: ISO 3166-1 alpha-3 (example: "USA")
    name: full country name in English
    native_name: native full country name
    """

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    alpha2: Mapped[str] = mapped_column(String(2), unique=True, nullable=False, index=True)
    alpha3: Mapped[str] = mapped_column(String(3), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    native_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)

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
        return (
            f"<CountryORM(id={self.id}, alpha2='{self.alpha2}', alpha3='{self.alpha3}', "
            f"name='{self.name}', native_name='{self.native_name}')>"
        )
