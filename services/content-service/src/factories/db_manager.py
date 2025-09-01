from typing import Annotated

from fastapi import Depends

from src.db import session_maker
from src.managers.db import DBManager
from src.protocols.db_manager import DBManagerProtocol


class DBManagerFactory:
    @classmethod
    def db_manager_factory(cls) -> DBManager:
        return DBManager(session_factory=session_maker)

    @classmethod
    async def get_db(cls):
        async with cls.db_manager_factory() as db:
            yield db


DBDep = Annotated[DBManagerProtocol, Depends(DBManagerFactory.get_db)]
