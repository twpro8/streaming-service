from typing import Annotated

from fastapi import Depends

from src.config import settings
from src.interfaces.storage import AbstractStorage
from src.adapters.s3_adapter import S3Adapter
from src.services.video import VideoService


class FileAdapterFactory:
    @staticmethod
    async def s3_adapter_factory() -> AbstractStorage:
        return S3Adapter(
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            bucket_name=settings.S3_BUCKET_NAME,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )


class VideoServiceFactory:
    @staticmethod
    async def video_service_factory(
        storage: Annotated[AbstractStorage, Depends(FileAdapterFactory.s3_adapter_factory)],
    ) -> VideoService:
        return VideoService(storage=storage)


VideoServiceDep = Annotated[VideoService, Depends(VideoServiceFactory.video_service_factory)]
