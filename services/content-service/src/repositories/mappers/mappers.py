from src.models import SeriesORM, SeasonORM, EpisodeORM, CommentORM, RatingORM, GenreORM
from src.repositories.mappers.base import DataMapper
from src.models.films import FilmORM
from src.schemas.comments import CommentDTO
from src.schemas.films import FilmDTO
from src.schemas.genres import GenreDTO
from src.schemas.rating import RatingDTO
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


class CommentDataMapper(DataMapper):
    db_model = CommentORM
    schema = CommentDTO


class RatingDataMapper(DataMapper):
    db_model = RatingORM
    schema = RatingDTO


class GenreDataMapper(DataMapper):
    db_model = GenreORM
    schema = GenreDTO
