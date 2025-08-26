from src.repositories.actors import ActorRepository, MovieActorRepository, ShowActorRepository
from src.repositories.comments import CommentRepository
from src.repositories.directors import DirectorRepository
from src.repositories.episodes import EpisodeRepository
from src.repositories.movies import MovieRepository
from src.repositories.genres import GenreRepository, MovieGenreRepository, ShowGenreRepository
from src.repositories.rating import RatingRepository
from src.repositories.seasons import SeasonRepository
from src.repositories.shows import ShowRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.movies = MovieRepository(self.session)
        self.shows = ShowRepository(self.session)
        self.seasons = SeasonRepository(self.session)
        self.episodes = EpisodeRepository(self.session)
        self.comments = CommentRepository(self.session)
        self.rating = RatingRepository(self.session)
        self.genres = GenreRepository(self.session)
        self.movies_genres = MovieGenreRepository(self.session)
        self.shows_genres = ShowGenreRepository(self.session)
        self.actors = ActorRepository(self.session)
        self.movies_actors = MovieActorRepository(self.session)
        self.shows_actors = ShowActorRepository(self.session)
        self.directors = DirectorRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
