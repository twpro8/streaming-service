import httpx


class BaseHttpAdapter:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get(self, path: str, params: dict = None):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{path}", params=params)
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, data: dict = None):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}{path}", json=data)
            response.raise_for_status()
            return response.json()
