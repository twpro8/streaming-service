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


class RepositoryFactory:
    def __init__(self, session):
        self.session = session
        self._repos = {}

    @property
    def movies(self):
        if "movies" not in self._repos:
            self._repos["movies"] = MovieRepository(self.session)
        return self._repos["movies"]

    @property
    def shows(self):
        if "shows" not in self._repos:
            self._repos["shows"] = ShowRepository(self.session)
        return self._repos["shows"]

    @property
    def seasons(self):
        if "seasons" not in self._repos:
            self._repos["seasons"] = SeasonRepository(self.session)
        return self._repos["seasons"]

    @property
    def episodes(self):
        if "episodes" not in self._repos:
            self._repos["episodes"] = EpisodeRepository(self.session)
        return self._repos["episodes"]

    @property
    def comments(self):
        if "comments" not in self._repos:
            self._repos["comments"] = CommentRepository(self.session)
        return self._repos["comments"]

    @property
    def rating(self):
        if "rating" not in self._repos:
            self._repos["rating"] = RatingRepository(self.session)
        return self._repos["rating"]

    @property
    def genres(self):
        if "genres" not in self._repos:
            self._repos["genres"] = GenreRepository(self.session)
        return self._repos["genres"]

    @property
    def movies_genres(self):
        if "movies_genres" not in self._repos:
            self._repos["movies_genres"] = MovieGenreRepository(self.session)
        return self._repos["movies_genres"]

    @property
    def shows_genres(self):
        if "shows_genres" not in self._repos:
            self._repos["shows_genres"] = ShowGenreRepository(self.session)
        return self._repos["shows_genres"]

    @property
    def actors(self):
        if "actors" not in self._repos:
            self._repos["actors"] = ActorRepository(self.session)
        return self._repos["actors"]

    @property
    def movies_actors(self):
        if "movies_actors" not in self._repos:
            self._repos["movies_actors"] = MovieActorRepository(self.session)
        return self._repos["movies_actors"]

    @property
    def shows_actors(self):
        if "shows_actors" not in self._repos:
            self._repos["shows_actors"] = ShowActorRepository(self.session)
        return self._repos["shows_actors"]

    @property
    def directors(self):
        if "directors" not in self._repos:
            self._repos["directors"] = DirectorRepository(self.session)
        return self._repos["directors"]

    @property
    def movies_directors(self):
        if "movies_directors" not in self._repos:
            self._repos["movies_directors"] = MovieDirectorRepository(self.session)
        return self._repos["movies_directors"]

    @property
    def shows_directors(self):
        if "shows_directors" not in self._repos:
            self._repos["shows_directors"] = ShowDirectorRepository(self.session)
        return self._repos["shows_directors"]

    @property
    def countries(self):
        if "countries" not in self._repos:
            self._repos["countries"] = CountryRepository(self.session)
        return self._repos["countries"]

    @property
    def movies_countries(self):
        if "movies_countries" not in self._repos:
            self._repos["movies_countries"] = MovieCountryRepository(self.session)
        return self._repos["movies_countries"]

    @property
    def shows_countries(self):
        if "shows_countries" not in self._repos:
            self._repos["shows_countries"] = ShowCountryRepository(self.session)
        return self._repos["shows_countries"]

    @property
    def languages(self):
        if "languages" not in self._repos:
            self._repos["languages"] = LanguageRepository(self.session)
        return self._repos["languages"]
