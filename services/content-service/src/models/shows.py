from typing import List
from uuid import UUID, uuid4
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, DECIMAL, UniqueConstraint, CheckConstraint, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base


class ShowORM(Base):
    __tablename__ = "shows"
    __table_args__ = (
        UniqueConstraint("title", "release_date", name="uq_show"),
        CheckConstraint("rating >= 0 AND rating <= 10"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(String(1024))
    release_date: Mapped[date]
    rating: Mapped[Decimal] = mapped_column(DECIMAL(3, 1), default=Decimal("0.0"))
    cover_url: Mapped[str | None] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )  # Make sure you have added the trigger to the migration.

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
