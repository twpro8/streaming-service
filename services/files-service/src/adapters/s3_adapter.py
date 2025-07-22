from contextlib import asynccontextmanager
from typing import List

from aiobotocore.session import get_session
from botocore.exceptions import ClientError, BotoCoreError

from src.config import settings
from src.interfaces.storage import AbstractStorage
from src.exceptions import (
    ObjectNotFoundException,
    UploadFailureException,
    FileTooLargeException,
)


MAX_SIZE = settings.MAX_FILE_SIZE
CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB
MIN_PART_SIZE = 5 * 1024 * 1024  # 5 MB


class S3Adapter(AbstractStorage):
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
    async def _get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_streaming_file(self, stream, key: str, max_file_size: int = MAX_SIZE):
        async with self._get_client() as client:
            response = await client.create_multipart_upload(Bucket=self.bucket_name, Key=key)
            upload_id = response["UploadId"]
            parts = []
            part_number = 1
            buffer = bytearray()
            total_uploaded = 0
            try:
                async for chunk in stream:
                    buffer.extend(chunk)
                    total_uploaded += len(chunk)
                    if total_uploaded > max_file_size:
                        await client.abort_multipart_upload(
                            Bucket=self.bucket_name,
                            Key=key,
                            UploadId=upload_id,
                        )
                        raise FileTooLargeException(
                            f"Uploaded file exceeds the allowed size limit: {max_file_size}"
                        )
                    if len(buffer) >= CHUNK_SIZE:
                        part = await self._upload_part(client, key, upload_id, part_number, buffer)
                        parts.append(part)
                        part_number += 1
                        buffer.clear()
                if buffer:
                    part = await self._upload_part(client, key, upload_id, part_number, buffer)
                    parts.append(part)
                await client.complete_multipart_upload(
                    Bucket=self.bucket_name,
                    Key=key,
                    UploadId=upload_id,
                    MultipartUpload={"Parts": parts},
                )
            except (ClientError, BotoCoreError) as exc:
                await client.abort_multipart_upload(
                    Bucket=self.bucket_name,
                    Key=key,
                    UploadId=upload_id,
                )
                raise UploadFailureException from exc

        return total_uploaded

    async def _upload_part(self, client, key, upload_id, part_number, data: bytes):
        resp = await client.upload_part(
            Bucket=self.bucket_name,
            Key=key,
            UploadId=upload_id,
            PartNumber=part_number,
            Body=data,
        )
        return {"ETag": resp["ETag"], "PartNumber": part_number}

    async def upload_file(self, key: str, data: bytes):
        try:
            async with self._get_client() as client:
                resp = await client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=data,
                )
                if resp.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200:
                    raise UploadFailureException
        except (ClientError, BotoCoreError) as exc:
            raise UploadFailureException from exc

    async def get_file(self, key: str) -> bytes:
        """
        Get object from s3 storage
        """
        async with self._get_client() as client:
            try:
                resp = await client.get_object(Bucket=self.bucket_name, Key=key)
                async with resp["Body"] as stream:
                    data = await stream.read()
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    raise ObjectNotFoundException(detail=f"File {key} not found")
                raise
        return data

    async def get_files_list(self, folder_path: str) -> List[dict]:
        """
        Get list of objects under the given folder path using paginator
        """
        objects = []

        async with self._get_client() as client:
            paginator = client.get_paginator("list_objects_v2")
            async for result in paginator.paginate(Bucket=self.bucket_name, Prefix=folder_path):
                contents = result.get("Contents", [])
                objects.extend(contents)

        return objects

    async def delete_file(self, key: str):
        async with self._get_client() as client:
            await client.delete_object(Bucket=self.bucket_name, Key=key)

    async def delete_dir(self, key: str) -> None:
        async with self._get_client() as client:
            paginator = client.get_paginator("list_objects_v2")
            async for page in paginator.paginate(Bucket=self.bucket_name, Prefix=key):
                if "Contents" not in page:
                    continue

                objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
                for i in range(0, len(objects), 1000):
                    chunk = objects[i : i + 1000]
                    await client.delete_objects(Bucket=self.bucket_name, Delete={"Objects": chunk})

    async def generate_presigned_url(self, key: str, expires: int = 3600) -> str | None:
        async with self._get_client() as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires,
            )
            return url
