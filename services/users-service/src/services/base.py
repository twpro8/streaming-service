from src.adapters.base import BaseRabbitAdapter
from src.adapters.content import ContentHTTPAdapter
from src.db import DBManager


class BaseService:
    db: DBManager = None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db
        self.http_adapter = ContentHTTPAdapter()
        self.rabbit_adapter = BaseRabbitAdapter()

    async def check_user_exists(self, **kwargs) -> bool:
        user = await self.db.users.get_one_or_none(**kwargs)
        return user is not None

    async def check_favorite_exists(self, **kwargs) -> bool:
        user = await self.db.favorites.get_one_or_none(**kwargs)
        return user is not None

    async def check_playlist_exists(self, **kwargs) -> bool:
        user = await self.db.playlists.get_one_or_none(**kwargs)
        return user is not None

    async def is_friend(self, user_id: int, friend_id: int) -> bool:
        friend = await self.db.friendships.get_one_or_none(user_id=user_id, friend_id=friend_id)
        return friend is not None

    async def check_content_exists(self, content_id: int, content_type: str) -> bool:
        return await self.http_adapter.content_exists(content_id, content_type)
