from typing import List
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import date, datetime

from sqlalchemy import String, DECIMAL, CheckConstraint, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base


class MovieORM(Base):
    __tablename__ = "movies"

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
    duration: Mapped[int]
    video_url: Mapped[str | None] = mapped_column(unique=True)
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
        secondary="movie_director_associations",
        back_populates="movies",
    )
    actors: Mapped[List["ActorORM"]] = relationship(
        secondary="movie_actor_associations",
        back_populates="movies",
    )
    genres: Mapped[List["GenreORM"]] = relationship(
        secondary="movie_genre_associations",
        back_populates="movies",
    )
    countries: Mapped[List["CountryORM"]] = relationship(
        secondary="movie_country_associations",
        back_populates="movies",
    )
    comments: Mapped[List["CommentORM"]] = relationship(back_populates="movie")
