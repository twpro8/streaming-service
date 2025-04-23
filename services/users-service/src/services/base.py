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
