import logging
from socket import AF_INET

import aiohttp

from src.config import settings


log = logging.getLogger(__name__)


class AiohttpClient:
    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    async def startup(self):
        timeout = aiohttp.ClientTimeout(total=2)
        connector = aiohttp.TCPConnector(
            family=AF_INET,
            limit_per_host=settings.SIZE_POOL_AIOHTTP,
        )
        self._session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            raise_for_status=True,
        )
        log.info("Aiohttp: client session created")
        return self

    async def shutdown(self):
        if self._session:
            await self._session.close()
            log.info("Aiohttp: client session closed")

    def _ensure_session(self):
        if self._session is None:
            raise RuntimeError("HTTPClient not started. Call startup() first.")

    async def get(self, url: str, **kwargs):
        self._ensure_session()
        async with self._session.get(url, **kwargs) as resp:
            return resp

    async def get_json(self, url: str, **kwargs):
        self._ensure_session()
        async with self._session.get(url, **kwargs) as resp:
            log.info(f"Aiohttp GET: got response with status code {resp.status}")
            return await resp.json(), resp

    async def post(self, url: str, data: dict):
        self._ensure_session()
        async with self._session.post(url=url, data=data) as resp:
            log.info(f"Aiohttp POST: got response with status code {resp.status}")
            return await resp.json()
