from src.models import SeriesORM, SeasonORM, EpisodeORM
from src.repositories.mappers.base import DataMapper
from src.models.films import FilmORM
from src.schemas.films import FilmDTO
from src.schemas.seasons import SeasonDTO
from src.schemas.series import SeriesDTO
from src.schemas.episodes import EpisodeDTO


class FilmDataMapper(DataMapper):
    db_model = FilmORM
    schema = FilmDTO


class SeriesDataMapper(DataMapper):
    db_model = SeriesORM
    schema = SeriesDTO


class SeasonDataMapper(DataMapper):
    db_model = SeasonORM
    schema = SeasonDTO


class EpisodeDataMapper(DataMapper):
    db_model = EpisodeORM
    schema = EpisodeDTO
