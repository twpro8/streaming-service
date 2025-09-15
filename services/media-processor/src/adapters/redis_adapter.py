import logging

import redis.asyncio as redis


class RedisAdapter:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self):
        logging.info(f"Connecting to Redis server at {self.host}:{self.port}...")
        self.redis = await redis.Redis(host=self.host, port=self.port)
        logging.info("Connected to Redis server.")

    async def set(self, key: str, value: str, expires: int = None):
        if expires:
            await self.redis.set(key, value, expires)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def delete_many(self, keys: list[str]):
        await self.redis.delete(*keys)

    async def close(self):
        if self.redis:
            await self.redis.close()
