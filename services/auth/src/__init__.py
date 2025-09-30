from src.config import settings
from src.managers.redis import RedisManager
from src.adapters.aiohttp import HTTPClient


redis_manager = RedisManager(url=settings.REDIS_URL)
aiohttp_client = HTTPClient()
