from src.config import settings
from src.adapters.s3_adapter import S3Adapter


class StorageAdapterFactory:
    @staticmethod
    async def s3_adapter_factory() -> S3Adapter:
        return S3Adapter(
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            bucket_name=settings.S3_BUCKET_NAME,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )

    @staticmethod
    def s3_adapter_sync_factory() -> S3Adapter:
        return S3Adapter(
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            bucket_name=settings.S3_BUCKET_NAME,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )
