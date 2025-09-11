import logging
from urllib.parse import urlparse

from redis.exceptions import ConnectionError, AuthenticationError
import redis.asyncio as redis
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


log = logging.getLogger(__name__)


class RedisManager:
    def __init__(self, url: str):
        self.url = url
        self.redis = None

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(ConnectionError),
    )
    async def connect(self):
        parsed = urlparse(self.url)
        log.info(f"Redis: Connecting to server at {parsed.hostname}:{parsed.port}...")
        self.redis = await redis.from_url(self.url, decode_responses=True)
        try:
            await self.redis.ping()
            log.info("Redis: Connected.")
        except AuthenticationError:
            log.error("Redis: Authentication failed.")
            raise
        except ConnectionError:
            log.error("Redis: Connection failed. Retrying...")
            raise

    async def set(self, key: str, value: str, expires: int | None = None):
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
            log.info("Redis: Connection closed.")
