from src import settings
from src.adapters.base import BaseHttpAdapter


class ContentHTTPAdapter:
    def __init__(self):
        self.client = BaseHttpAdapter(base_url=settings.CONTENT_SERVICE_URL)

    async def get_films_by_ids(self, film_ids: list[int]):
        if film_ids:
            return await self.client.get("/films", params={"ids": film_ids})

    async def get_series_by_ids(self, series_ids: list[int]):
        return await self.client.get("/series", params={"ids": series_ids})

    async def content_exists(self, content_id: int, content_type: str) -> bool:
        url = f"/{content_type}/{content_id}/exists"
        status_code = await self.client.get_status_code(path=url)
        if status_code == 200:
            return True
        elif status_code == 404:
            return False
