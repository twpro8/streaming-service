from src.db import DBManager
from src.interfaces.storage import AbstractStorage


class BaseService:
    db: DBManager = None

    def __init__(self, db: DBManager | None = None, storage: AbstractStorage | None = None) -> None:
        self.db = db
        self.storage = storage
