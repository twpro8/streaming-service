from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import settings
from src.repositories.comments import CommentRepository
from src.repositories.films import FilmRepository
from src.repositories.genres import GenreRepository, FilmGenreRepository, SeriesGenreRepository
from src.repositories.rating import RatingRepository
from src.repositories.seasons import SeasonRepository
from src.repositories.series import SeriesRepository
from src.repositories.episodes import EpisodeRepository


engine = create_async_engine(url=settings.DB_URL)
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

null_pool_engine = create_async_engine(url=settings.DB_URL, poolclass=NullPool)
null_pool_session_maker = async_sessionmaker(bind=null_pool_engine, expire_on_commit=False)


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.films = FilmRepository(self.session)
        self.series = SeriesRepository(self.session)
        self.seasons = SeasonRepository(self.session)
        self.episodes = EpisodeRepository(self.session)
        self.comments = CommentRepository(self.session)
        self.rating = RatingRepository(self.session)
        self.genres = GenreRepository(self.session)
        self.films_genres = FilmGenreRepository(self.session)
        self.series_genres = SeriesGenreRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
