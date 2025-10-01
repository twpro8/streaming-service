from src.managers.db import DBManager
from src.managers.redis import RedisManager
from src.adapters.aiohttp import HTTPClient


class BaseService:
    db: DBManager | None
    redis: RedisManager | None
    ac: HTTPClient | None

    def __init__(
        self,
        db: DBManager | None = None,
        redis: RedisManager | None = None,
        ac: HTTPClient | None = None,
    ) -> None:
        self.db = db
        self.redis = redis
        self.ac = ac
