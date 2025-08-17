# ruff: noqa

from typing import List
from uuid import UUID, uuid4
from datetime import date
from decimal import Decimal

from sqlalchemy import String, DECIMAL, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base


class SeriesORM(Base):
    __tablename__ = "series"
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(512))
    director: Mapped[str] = mapped_column(String(255))
    release_year: Mapped[date]
    rating: Mapped[Decimal] = mapped_column(
        DECIMAL(3, 1),
        CheckConstraint("rating >= 0 AND rating <= 10"),
        default=Decimal("0.0"),
    )
    cover_url: Mapped[str | None] = mapped_column(unique=True)

    # Relationships
    seasons: Mapped[List["SeasonORM"]] = relationship(back_populates="series")
    comments: Mapped[List["CommentORM"]] = relationship(back_populates="series")
    genres: Mapped[List["GenreORM"]] = relationship(
        secondary="series_genre_associations",
        back_populates="series",
    )
    actors: Mapped[List["ActorORM"]] = relationship(
        secondary="series_actor_associations", back_populates="series"
    )


class SeasonORM(Base):
    __tablename__ = "seasons"
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    series_id: Mapped[UUID] = mapped_column(ForeignKey("series.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    season_number: Mapped[int]

    # Relationships
    series: Mapped["SeriesORM"] = relationship(back_populates="seasons")
    episodes: Mapped[List["EpisodeORM"]] = relationship(back_populates="season")

    __table_args__ = (
        UniqueConstraint("series_id", "season_number", name="unique_season_per_series"),
    )


class EpisodeORM(Base):
    __tablename__ = "episodes"
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    series_id: Mapped[UUID] = mapped_column(ForeignKey("series.id", ondelete="CASCADE"))
    season_id: Mapped[UUID] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    episode_number: Mapped[int]
    duration: Mapped[int]
    video_url: Mapped[str | None] = mapped_column(unique=True)

    # Relationships
    series: Mapped["SeriesORM"] = relationship()
    season: Mapped["SeasonORM"] = relationship(back_populates="episodes")

    __table_args__ = (
        UniqueConstraint("season_id", "episode_number", name="unique_episode_per_season"),
    )
