import re
from contextlib import asynccontextmanager
from typing import Optional

from aiobotocore.session import get_session


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
        self, filename: str, content_type: str, content_id: int, data: bytes
    ) -> str:

        key = f"{content_type}/{content_id}/{self.sanitize_filename(filename)}"

        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
            )

        return key

    async def generate_presigned_url(
        self, filename: str, content_type: str, content_id: int, expires: int = 3600
    ) -> Optional[str]:

        key = f"{content_type}/{content_id}/{self.sanitize_filename(filename)}"

        async with self.get_client() as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires,
            )
            return url

    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 50) -> str:
        """
        Sanitize a filename by removing invalid characters and truncating its base name.
        """

        if "." not in filename:
            raise ValueError("Filename must contain an extension.")

        name, ext = filename.rsplit(".", 1)
        name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)

        return f"{name[:max_length]}.{ext}"
