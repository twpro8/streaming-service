from typing import List
from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk, created_at, str_256, str_1024


class ShowORM(Base):
    __tablename__ = "shows"
    __table_args__ = (
        UniqueConstraint("title", "release_date", name="uq_show"),
        CheckConstraint("rating >= 0 AND rating <= 10"),
    )

    id: Mapped[uuid_pk]
    title: Mapped[str_256]
    description: Mapped[str_1024]
    release_date: Mapped[date]
    rating: Mapped[Decimal] = mapped_column(DECIMAL(3, 1), default=Decimal("0.0"))
    cover_url: Mapped[str | None] = mapped_column(unique=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[created_at]  # Make sure you have added the trigger to the migration.

    # Relationships
    directors: Mapped[List["DirectorORM"]] = relationship(
        secondary="show_director_associations",
        back_populates="shows",
    )
    actors: Mapped[List["ActorORM"]] = relationship(
        secondary="show_actor_associations",
        back_populates="shows",
    )
    genres: Mapped[List["GenreORM"]] = relationship(
        secondary="show_genre_associations",
        back_populates="shows",
    )
    countries: Mapped[List["CountryORM"]] = relationship(
        secondary="show_country_associations",
        back_populates="shows",
    )
    seasons: Mapped[List["SeasonORM"]] = relationship(back_populates="show")
