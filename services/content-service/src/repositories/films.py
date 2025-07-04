from src.models import FilmORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FilmDataMapper
from src.schemas.films import FilmDTO


class FilmRepository(BaseRepository):
    model = FilmORM
    schema = FilmDTO
    mapper = FilmDataMapper
