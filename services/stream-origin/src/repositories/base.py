from botocore.exceptions import ClientError

from src.adapters.s3 import S3Client
from src.exceptions import ObjectNotFoundException


class BaseS3Repository:
    def __init__(self, s3_client: S3Client):
        self.s3 = s3_client

    async def get_one(self, key: str) -> bytes:
        try:
            obj = await self.s3.get_file(key)
        except ClientError:
            raise ObjectNotFoundException
        return obj

    async def get_tmp_url(self, key: str, expires: int = 3600) -> str:
        try:
            url = await self.s3.generate_presigned_url(key, expires)
        except ClientError:
            raise ObjectNotFoundException
        return url

    async def upload(self, key: str, file: bytes) -> bool:
        return await self.s3.upload_file(key, file)

    async def delete(self, key: str):
        await self.s3.delete_file(key)

    async def delete_all(self, key: str):
        await self.s3.delete_bulk(key)
