from src.db import DBManager
from src.adapters.rabbit_adapter import RabbitAdapter


class BaseService:
    db: DBManager = None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db
        self.rabbit_adapter = RabbitAdapter()
