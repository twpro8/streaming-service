from typing import Callable

import httpx

from src import rabbitmq_manager


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

    async def get_status_code(self, path: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{path}")
            return response.status_code


class BaseRabbitAdapter:
    def __init__(self):
        self.rabbit = rabbitmq_manager

    async def send_message(self, queue_name: str, message: str):
        await self.rabbit.publish(queue_name, message)

    async def receive_message(self, queue_name, func: Callable):
        await self.rabbit.start_consumer(queue_name, func)
