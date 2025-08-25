# ruff: noqa

from datetime import datetime, date
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import DateTime, text, String, UniqueConstraint, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base
from src.enums import ZodiacSign


class ActorORM(Base):
    __tablename__ = "actors"
    __table_args__ = (
        UniqueConstraint(
            "first_name",
            "last_name",
            "birth_date",
            name="unique_actors_full_identity",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    first_name: Mapped[str] = mapped_column(String(48))
    last_name: Mapped[str] = mapped_column(String(48))
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    zodiac_sign: Mapped[ZodiacSign | None] = mapped_column(Enum(ZodiacSign), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )

    # Relationships
    movies: Mapped[List["MovieORM"]] = relationship(
        secondary="movie_actor_associations",
        back_populates="actors",
    )
    shows: Mapped[List["ShowORM"]] = relationship(
        secondary="show_actor_associations",
        back_populates="actors",
    )


class MovieActorORM(Base):
    __tablename__ = "movie_actor_associations"

    movie_id: Mapped[UUID] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    actor_id: Mapped[UUID] = mapped_column(
        ForeignKey("actors.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ShowActorORM(Base):
    __tablename__ = "show_actor_associations"

    show_id: Mapped[UUID] = mapped_column(
        ForeignKey("shows.id", ondelete="CASCADE"),
        primary_key=True,
    )
    actor_id: Mapped[UUID] = mapped_column(
        ForeignKey("actors.id", ondelete="CASCADE"),
        primary_key=True,
    )
