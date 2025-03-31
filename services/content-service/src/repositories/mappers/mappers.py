from src.repositories.mappers.base import DataMapper
from src.models.films import FilmORM
from src.schemas.films import FilmDTO


class FilmDataMapper(DataMapper):
    db_model = FilmORM
    schema = FilmDTO
