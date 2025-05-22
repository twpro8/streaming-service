from contextlib import asynccontextmanager

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
    async def _get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, key: str, data: bytes) -> bool:
        async with self._get_client() as client:
            resp = await client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
            )
            status_code = resp.get("ResponseMetadata", {}).get("HTTPStatusCode")

        return True if status_code == 200 else False

    async def get_file(self, key: str) -> bytes:
        """
        Get object from s3
        """
        async with self._get_client() as client:
            resp = await client.get_object(Bucket=self.bucket_name, Key=key)
            # This will ensure the connection is correctly re-used/closed
            async with resp["Body"] as stream:
                data = await stream.read()
            return data

    async def get_files_list(self, folder_path: str) -> list[dict]:
        """
        Get list of S3 objects under the given folder path using paginator
        """
        objects = []

        async with self._get_client() as client:
            paginator = client.get_paginator("list_objects_v2")
            async for result in paginator.paginate(Bucket=self.bucket_name, Prefix=folder_path):
                contents = result.get("Contents", [])
                objects.extend(contents)

        return objects

    async def delete_file(self, key: str) -> bool:
        async with self._get_client() as client:
            resp = await client.delete_object(Bucket=self.bucket_name, Key=key)
            status_code = resp.get("ResponseMetadata", {}).get("HTTPStatusCode")

            return True if status_code == 204 else False

    async def delete_bulk(self, key: str) -> None:
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
