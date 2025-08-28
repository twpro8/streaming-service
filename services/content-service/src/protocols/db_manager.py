from typing import Protocol

from src.repositories.actors import (
    ActorRepository,
    MovieActorRepository,
    ShowActorRepository,
)
from src.repositories.comments import CommentRepository
from src.repositories.countries import (
    CountryRepository,
    MovieCountryRepository,
    ShowCountryRepository,
)
from src.repositories.directors import (
    DirectorRepository,
    MovieDirectorRepository,
    ShowDirectorRepository,
)
from src.repositories.episodes import EpisodeRepository
from src.repositories.languages import LanguageRepository
from src.repositories.movies import MovieRepository
from src.repositories.genres import (
    GenreRepository,
    MovieGenreRepository,
    ShowGenreRepository,
)
from src.repositories.rating import RatingRepository
from src.repositories.seasons import SeasonRepository
from src.repositories.shows import ShowRepository


class DBManagerProtocol(Protocol):
    movies: MovieRepository
    shows: ShowRepository
    seasons: SeasonRepository
    episodes: EpisodeRepository
    comments: CommentRepository
    rating: RatingRepository
    genres: GenreRepository
    movies_genres: MovieGenreRepository
    shows_genres: ShowGenreRepository
    actors: ActorRepository
    movies_actors: MovieActorRepository
    shows_actors: ShowActorRepository
    directors: DirectorRepository
    movies_directors: MovieDirectorRepository
    shows_directors: ShowDirectorRepository
    countries: CountryRepository
    movies_countries: MovieCountryRepository
    shows_countries: ShowCountryRepository
    languages: LanguageRepository

    async def commit(self): ...
    async def rollback(self): ...
