from typing import Annotated

from fastapi import Depends

from src.factories.file_adapter_factories import FileAdapterFactory
from src.files.service import FileService
from src.interfaces.storage import AbstractStorage


class FileServiceFactory:
    @staticmethod
    async def file_service_factory(
            storage: Annotated[AbstractStorage, Depends(FileAdapterFactory.s3_adapter_factory)]
    ) -> FileService:
        return FileService(storage=storage)
