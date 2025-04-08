from src.connectors.rabbit_conn import RabbitManager
from src.config import settings


rabbitmq_manager = RabbitManager(amqp_url=settings.RABBITMQ_URL)
