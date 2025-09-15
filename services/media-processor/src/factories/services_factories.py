from typing import Annotated

from fastapi import Depends

from src.factories.db_manager_factories import DBManagerFactory
from src.factories.storage_adapter_factories import StorageAdapterFactory
from src.interfaces.storage import AbstractStorage
from src.services.auth import AuthService
from src.services.images import ImageService
from src.services.videos import VideoService
from src.utils.db_manager import DBManager


class VideoServiceFactory:
    @staticmethod
    async def video_service_factory(
        db: Annotated[DBManager, Depends(DBManagerFactory.get_db)],
        storage: Annotated[AbstractStorage, Depends(StorageAdapterFactory.s3_adapter_factory)],
    ) -> VideoService:
        return VideoService(db=db, storage=storage)


class ImageServiceFactory:
    @staticmethod
    async def image_service_factory(
        db: Annotated[DBManager, Depends(DBManagerFactory.get_db)],
        storage: Annotated[AbstractStorage, Depends(StorageAdapterFactory.s3_adapter_factory)],
    ) -> ImageService:
        return ImageService(db=db, storage=storage)


class AuthServiceFactory:
    @staticmethod
    async def auth_service_factory() -> AuthService:
        return AuthService()
