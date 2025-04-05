from src.models import SeriesORM
from src.repositories.mappers.base import DataMapper
from src.models.films import FilmORM
from src.schemas.films import FilmDTO
from src.schemas.series import SeriesDTO


class FilmDataMapper(DataMapper):
    db_model = FilmORM
    schema = FilmDTO


class SeriesDataMapper(DataMapper):
    db_model = SeriesORM
    schema = SeriesDTO
