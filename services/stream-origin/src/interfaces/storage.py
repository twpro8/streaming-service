from abc import ABC, abstractmethod
from typing import List


class AbstractStorage(ABC):
    @abstractmethod
    async def get_file(self, key: str) -> bytes: ...

    @abstractmethod
    async def get_files_list(self, folder_path: str) -> List[dict]: ...

    @abstractmethod
    async def upload_file(self, key: str, data: bytes) -> bool: ...

    @abstractmethod
    async def delete_file(self, key: str): ...

    @abstractmethod
    async def delete_bulk(self, key: str) -> None: ...

    @abstractmethod
    async def generate_presigned_url(self, key: str, expires: int = 3600) -> str | None: ...
