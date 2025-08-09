from typing import List

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.exceptions import GenreNotFoundException
from src.models import GenreORM, FilmGenreORM, SeriesGenreORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    GenreDataMapper,
    FilmGenreDataMapper,
    SeriesGenreDataMapper,
)
from src.schemas.genres import GenreDTO, FilmGenreDTO, SeriesGenreDTO


class GenreRepository(BaseRepository):
    model = GenreORM
    schema = GenreDTO
    mapper = GenreDataMapper


class FilmGenreRepository(BaseRepository):
    model = FilmGenreORM
    schema = FilmGenreDTO
    mapper = FilmGenreDataMapper

    async def add_film_genres(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise GenreNotFoundException from exc


class SeriesGenreRepository(BaseRepository):
    model = SeriesGenreORM
    schema = SeriesGenreDTO
    mapper = SeriesGenreDataMapper

    async def add_series_genres(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise GenreNotFoundException from exc
