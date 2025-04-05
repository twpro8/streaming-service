from src.adapters.base import BaseHttpAdapter


class ContentAdapter:
    def __init__(self, service_url: str):
        self.client = BaseHttpAdapter(service_url)

    async def get_films_by_ids(self, film_ids: list[int]):
        return await self.client.get("/films", params={"ids": film_ids})

    async def get_series_by_ids(self, series_ids: list[int]):
        return await self.client.get("/series", params={"ids": series_ids})

    async def film_exists(self, film_id: int):
        response = await self.client.get(f"/films/{film_id}/exists")
        return response.get("exists", False)
