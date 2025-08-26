from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class MovieDirectorORM(Base):
    __tablename__ = "movie_director_associations"

    movie_id: Mapped[UUID] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    director_id: Mapped[int] = mapped_column(
        ForeignKey("directors.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ShowDirectorORM(Base):
    __tablename__ = "show_director_associations"

    show_id: Mapped[UUID] = mapped_column(
        ForeignKey("shows.id", ondelete="CASCADE"),
        primary_key=True,
    )
    director_id: Mapped[int] = mapped_column(
        ForeignKey("directors.id", ondelete="CASCADE"),
        primary_key=True,
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


class MovieGenreORM(Base):
    __tablename__ = "movie_genre_associations"

    movie_id: Mapped[UUID] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ShowGenreORM(Base):
    __tablename__ = "show_genre_associations"

    show_id: Mapped[UUID] = mapped_column(
        ForeignKey("shows.id", ondelete="CASCADE"),
        primary_key=True,
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    )


class MovieCountryORM(Base):
    __tablename__ = "movie_country_associations"

    movie_id: Mapped[UUID] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ShowCountryORM(Base):
    __tablename__ = "show_country_associations"

    show_id: Mapped[UUID] = mapped_column(
        ForeignKey("shows.id", ondelete="CASCADE"),
        primary_key=True,
    )
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"),
        primary_key=True,
    )
