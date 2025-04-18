from src.connectors.redis_conn import RedisManager
from src.connectors.rabbit_conn import RabbitManager
from src.config import settings


redis_manager = RedisManager(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
)
rabbitmq_manager = RabbitManager(amqp_url=settings.RABBITMQ_URL)
