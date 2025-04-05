from src.adapters.service import ServiceAdapter
from src.db import DBManager


class BaseService:
    db: DBManager = None

    def __init__(self, db: DBManager | None = None, adapter: ServiceAdapter | None = None) -> None:
        self.db = db
        self.adapter = adapter
