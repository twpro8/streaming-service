from src import rabbitmq_manager
from src.adapters.rabbitmq import RabbitAdapter
from src.db import DBManager


rabbit_publisher = RabbitAdapter(exchange_name="events", rabbit=rabbitmq_manager)


class BaseAppService:
    def __init__(self, db: DBManager | None = None):
        self.db = db
        self.publisher = rabbit_publisher
