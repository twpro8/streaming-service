from src.factories.db_manager import DBDep
from src.services.actors import ActorService
from src.services.comments import CommentService
from src.services.countries import CountryService
from src.services.directors import DirectorService
from src.services.episodes import EpisodeService
from src.services.genres import GenreService
from src.services.languages import LanguageService
from src.services.movies import MovieService
from src.services.rating import RatingService
from src.services.seasons import SeasonService
from src.services.shows import ShowService


class ServiceFactory:
    @staticmethod
    def movie_service_factory(db: DBDep) -> MovieService:
        return MovieService(db)

    @staticmethod
    def show_service_factory(db: DBDep) -> ShowService:
        return ShowService(db)

    @staticmethod
    def season_service_factory(db: DBDep) -> SeasonService:
        return SeasonService(db)

    @staticmethod
    def episode_service_factory(db: DBDep) -> EpisodeService:
        return EpisodeService(db)

    @staticmethod
    def director_service_factory(db: DBDep) -> DirectorService:
        return DirectorService(db)

    @staticmethod
    def actor_service_factory(db: DBDep) -> ActorService:
        return ActorService(db)

    @staticmethod
    def genre_service_factory(db: DBDep) -> GenreService:
        return GenreService(db)

    @staticmethod
    def country_service_factory(db: DBDep) -> CountryService:
        return CountryService(db)

    @staticmethod
    def language_service_factory(db: DBDep) -> LanguageService:
        return LanguageService(db)

    @staticmethod
    def rating_service_factory(db: DBDep) -> RatingService:
        return RatingService(db)

    @staticmethod
    def comment_service_factory(db: DBDep) -> CommentService:
        return CommentService(db)
