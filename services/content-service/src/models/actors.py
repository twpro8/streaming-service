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
        DateTime(timezone=True), server_default=text("TIMEZONE('UTC', now())"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('UTC', now())"), nullable=False
    )

    # Relationships
    films: Mapped[List["FilmORM"]] = relationship(
        secondary="film_actor_associations", back_populates="actors"
    )
    series: Mapped[List["SeriesORM"]] = relationship(
        secondary="series_actor_associations", back_populates="actors"
    )


class FilmActorORM(Base):
    __tablename__ = "film_actor_associations"
    film_id: Mapped[UUID] = mapped_column(
        ForeignKey("films.id", ondelete="CASCADE"), primary_key=True
    )
    actor_id: Mapped[UUID] = mapped_column(
        ForeignKey("actors.id", ondelete="CASCADE"), primary_key=True
    )


class SeriesActorORM(Base):
    __tablename__ = "series_actor_associations"
    series_id: Mapped[UUID] = mapped_column(
        ForeignKey("series.id", ondelete="CASCADE"), primary_key=True
    )
    actor_id: Mapped[UUID] = mapped_column(
        ForeignKey("actors.id", ondelete="CASCADE"), primary_key=True
    )
