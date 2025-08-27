from src.models.languages import LanguageORM
from src.models.countries import CountryORM
from src.models.actors import ActorORM
from src.models.genres import GenreORM
from src.models.rating import RatingORM
from src.models.comments import CommentORM
from src.models.episodes import EpisodeORM
from src.models.seasons import SeasonORM
from src.models.shows import ShowORM
from src.models.directors import DirectorORM
from src.models.associations import MovieActorORM, ShowActorORM
from src.repositories.mappers.base import DataMapper
from src.models.movies import MovieORM
from src.schemas.actors import ActorDTO, MovieActorDTO, ShowActorDTO
from src.schemas.comments import CommentDTO
from src.schemas.countries import CountryDTO
from src.schemas.directors import DirectorDTO
from src.schemas.languages import LanguageDTO
from src.schemas.movies import MovieDTO, MovieWithRelsDTO
from src.schemas.genres import GenreDTO, MovieGenreDTO, ShowGenreDTO
from src.schemas.rating import RatingDTO
from src.schemas.seasons import SeasonDTO
from src.schemas.shows import ShowDTO, ShowWithRelsDTO
from src.schemas.episodes import EpisodeDTO


class MovieDataMapper(DataMapper):
    db_model = MovieORM
    schema = MovieDTO


class ShowDataMapper(DataMapper):
    db_model = ShowORM
    schema = ShowDTO


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


class MovieGenreDataMapper(DataMapper):
    db_model = GenreORM
    schema = MovieGenreDTO


class ShowGenreDataMapper(DataMapper):
    db_model = ShowORM
    schema = ShowGenreDTO


class MovieWithRelsDataMapper(DataMapper):
    db_model = MovieORM
    schema = MovieWithRelsDTO


class ShowWithRelsDataMapper(DataMapper):
    db_model = ShowORM
    schema = ShowWithRelsDTO


class ActorDataMapper(DataMapper):
    db_model = ActorORM
    schema = ActorDTO


class MovieActorDataMapper(DataMapper):
    db_model = MovieActorORM
    schema = MovieActorDTO


class ShowActorDataMapper(DataMapper):
    db_model = ShowActorORM
    schema = ShowActorDTO


class DirectorDataMapper(DataMapper):
    db_model = DirectorORM
    schema = DirectorDTO


class CountryDataMapper(DataMapper):
    db_model = CountryORM
    schema = CountryDTO


class LanguageDataMapper(DataMapper):
    db_model = LanguageORM
    schema = LanguageDTO
