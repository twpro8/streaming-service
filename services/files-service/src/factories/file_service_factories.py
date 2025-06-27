from typing import Annotated

from fastapi import Depends

from src.db import session_maker
from src.factories.file_adapter_factories import FileAdapterFactory
from src.files.service import FileService
from src.interfaces.storage import AbstractStorage
from src.utils.db_manager import DBManager


class DBManagerFactory:
    @staticmethod
    def db_manager_factory():
        return DBManager(session_factory=session_maker)

    @classmethod
    async def get_db(cls):
        async with cls.db_manager_factory() as db:
            yield db


class FileServiceFactory:
    @staticmethod
    async def file_service_factory(
        db: Annotated[DBManager, Depends(DBManagerFactory.get_db)],
        storage: Annotated[AbstractStorage, Depends(FileAdapterFactory.s3_adapter_factory)],
    ) -> FileService:
        return FileService(db=db, storage=storage)
