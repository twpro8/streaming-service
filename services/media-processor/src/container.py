from src.config import settings
from src.adapters.redis_adapter import RedisAdapter

redis_manager = RedisAdapter(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
)
