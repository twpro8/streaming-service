from typing import List
from uuid import UUID, uuid4
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, DECIMAL, CheckConstraint, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base


class ShowORM(Base):
    __tablename__ = "shows"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(512))
    release_year: Mapped[date]
    rating: Mapped[Decimal] = mapped_column(
        DECIMAL(3, 1),
        CheckConstraint("rating >= 0 AND rating <= 10"),
        default=Decimal("0.0"),
    )
    cover_url: Mapped[str | None] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )

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
    comments: Mapped[List["CommentORM"]] = relationship(back_populates="show")
