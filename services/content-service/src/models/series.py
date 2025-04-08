from datetime import date
from typing import List

from sqlalchemy import String, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class SeriesORM(Base):
    __tablename__ = "series"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(512))
    director: Mapped[str] = mapped_column(String(255))
    release_year: Mapped[date]
    rating: Mapped[float] = mapped_column(DECIMAL(3, 1))
    cover_id: Mapped[int | None]

    # Relationships
    seasons: Mapped[List["SeasonORM"]] = relationship(back_populates="series")


class SeasonORM(Base):
    __tablename__ = "seasons"
    id: Mapped[int] = mapped_column(primary_key=True)
    series_id: Mapped[int] = mapped_column(ForeignKey("series.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    season_number: Mapped[int]

    # Relationships
    series: Mapped["SeriesORM"] = relationship(back_populates="seasons")
    episodes: Mapped[List["EpisodeORM"]] = relationship(back_populates="season")


class EpisodeORM(Base):
    __tablename__ = "episodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    series_id: Mapped[int] = mapped_column(ForeignKey("series.id", ondelete="CASCADE"))
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"))
    title: Mapped[str] = mapped_column(String(255))
    episode_number: Mapped[int]
    duration: Mapped[int]
    file_id: Mapped[int | None]

    # Relationships
    series: Mapped["SeriesORM"] = relationship()
    season: Mapped["SeasonORM"] = relationship(back_populates="episodes")
