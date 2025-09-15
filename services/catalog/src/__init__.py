from src.config import settings
from src.managers.redis import RedisManager


redis_manager = RedisManager(url=settings.REDIS_URL)
