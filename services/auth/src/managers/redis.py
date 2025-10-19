import logging
from urllib.parse import urlparse

from redis.exceptions import ConnectionError, AuthenticationError, TimeoutError, RedisError
import redis.asyncio as redis
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from src.exceptions import (
    RedisAuthenticationException,
    RedisConnectionException,
    RedisManagerException,
    RedisOperationException,
)


log = logging.getLogger(__name__)


class RedisManager:
    def __init__(self, url: str):
        self.url = url
        self.redis: redis.Redis | None = None

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(ConnectionError),
    )
    async def connect(self):
        parsed = urlparse(self.url)
        log.info(f"Redis: Connecting to server at {parsed.hostname}:{parsed.port}...")
        try:
            self.redis = await redis.from_url(self.url, decode_responses=True)
            await self.redis.ping()
            log.info("Redis: Connected successfully")
        except AuthenticationError as e:
            log.error("Redis: Authentication failed")
            raise RedisAuthenticationException from e
        except ConnectionError as e:
            log.error("Redis: Connection failed. Retrying...")
            raise RedisConnectionException from e
        except Exception as e:
            log.exception("Redis: Unexpected error during connection")
            raise RedisManagerException(f"Unexpected Redis error: {e}") from e

    async def set(self, key: str, value: str, expire: int | None = None):
        try:
            if expire:
                await self.redis.set(key, value, ex=expire)
            else:
                await self.redis.set(key, value)
        except (ConnectionError, TimeoutError, RedisError) as e:
            log.error(f"Redis: Failed to set key '{key}': {e}")
            raise RedisOperationException(f"Failed to set key '{key}'") from e

    async def get(self, key: str):
        try:
            return await self.redis.get(key)
        except (ConnectionError, TimeoutError, RedisError) as e:
            log.error(f"Redis: Failed to get key '{key}': {e}")
            raise RedisOperationException(f"Failed to get key '{key}'") from e

    async def delete(self, key: str):
        try:
            await self.redis.delete(key)
        except (ConnectionError, TimeoutError, RedisError) as e:
            log.error(f"Redis: Failed to delete key '{key}': {e}")
            raise RedisOperationException(f"Failed to delete key '{key}'") from e

    async def delete_many(self, keys: list[str]):
        try:
            await self.redis.delete(*keys)
        except (ConnectionError, TimeoutError, RedisError) as e:
            log.error(f"Redis: Failed to delete keys {keys}: {e}")
            raise RedisOperationException("Failed to delete multiple keys") from e

    async def close(self):
        if self.redis:
            try:
                await self.redis.close()
                log.info("Redis: Connection closed")
            except Exception as e:
                log.warning(f"Redis: Error closing connection: {e}")
