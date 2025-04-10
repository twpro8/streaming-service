from typing import List

from src import settings
from src.adapters.base import BaseHttpAdapter
from src.schemas.favorites import ContentType


class ContentHTTPAdapter:
    def __init__(self):
        self.client = BaseHttpAdapter(base_url=settings.CONTENT_SERVICE_URL)

    async def get_content_by_ids(self, ids: List[int], content_type: ContentType):
        if ids:
            data = await self.client.get(f"/{content_type}", params={"ids": ids})
            return data["data"]
        return []

    async def content_exists(self, content_id: int, content_type: str) -> bool:
        url = f"/{content_type}/{content_id}/exists"
        status_code = await self.client.get_status_code(path=url)
        return True if status_code == 200 else False
