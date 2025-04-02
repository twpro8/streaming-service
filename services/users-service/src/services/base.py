from httpx import AsyncClient

from src.db import DBManager


class BaseService:
    db: DBManager = None

    def __init__(self, db: DBManager | None = None, ac: AsyncClient | None = None) -> None:
        self.db = db
        self.ac = ac
