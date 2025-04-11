from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import settings
from src.repositories.films import FilmRepository
from src.repositories.seasons import SeasonRepository
from src.repositories.series import SeriesRepository


engine = create_async_engine(url=settings.DB_URL)
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.films = FilmRepository(self.session)
        self.series = SeriesRepository(self.session)
        self.seasons = SeasonRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
