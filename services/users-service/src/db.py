from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import settings
from src.repositories.favorites import FavoritesRepository
from src.repositories.friendship import FriendshipRepository
from src.repositories.playlists import PlaylistRepository
from src.repositories.users import UsersRepository

engine = create_async_engine(url=settings.DB_URL)
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

null_pool_engine = create_async_engine(url=settings.DB_URL, poolclass=NullPool)
null_pool_session_maker = async_sessionmaker(bind=null_pool_engine, expire_on_commit=False)


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.users = UsersRepository(self.session)
        self.friendships = FriendshipRepository(self.session)
        self.favorites = FavoritesRepository(self.session)
        self.playlists = PlaylistRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
