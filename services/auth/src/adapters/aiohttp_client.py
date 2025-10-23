import logging
from socket import AF_INET
from asyncio import TimeoutError

import aiohttp
from aiohttp import (
    ClientConnectionError,
    ClientResponseError,
    ClientPayloadError,
    ServerTimeoutError,
)

from src.config import settings
from src.exceptions import (
    AiohttpClientException,
    AiohttpNotInitializedException,
    AiohttpConnectionException,
    AiohttpTimeoutException,
    AiohttpResponseException,
)


log = logging.getLogger(__name__)


class AiohttpClient:
    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    async def startup(self):
        try:
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
        except Exception as e:
            log.exception("Aiohttp: failed to create client session")
            raise AiohttpClientException("Failed to initialize aiohttp client") from e

    async def shutdown(self):
        if self._session:
            try:
                await self._session.close()
                log.info("Aiohttp: client session closed")
            except Exception as e:
                log.warning(f"Aiohttp: error while closing session: {e}")

    def _ensure_session(self):
        if self._session is None:
            raise AiohttpNotInitializedException("HTTPClient not started. Call startup() first.")

    async def get(self, url: str, **kwargs):
        self._ensure_session()
        try:
            async with self._session.get(url, **kwargs) as resp:
                log.info(f"Aiohttp GET {url}: status {resp.status}")
                return resp
        except ClientConnectionError as e:
            log.error(f"Aiohttp: connection error while GET {url}: {e}")
            raise AiohttpConnectionException(f"Connection error while GET {url}") from e
        except (TimeoutError, ServerTimeoutError) as e:
            log.error(f"Aiohttp: timeout while GET {url}")
            raise AiohttpTimeoutException(f"Timeout while GET {url}") from e
        except ClientResponseError as e:
            log.error(f"Aiohttp: bad response while GET {url}: {e}")
            raise AiohttpResponseException(f"Bad response while GET {url}: {e.status}") from e
        except ClientPayloadError as e:
            log.error(f"Aiohttp: payload error while GET {url}: {e}")
            raise AiohttpResponseException(f"Payload error while GET {url}") from e
        except Exception as e:
            log.exception(f"Aiohttp: unexpected error while GET {url}")
            raise AiohttpClientException(f"Unexpected error while GET {url}") from e

    async def get_json(self, url: str, **kwargs):
        self._ensure_session()
        try:
            async with self._session.get(url, **kwargs) as resp:
                log.info(f"Aiohttp GET {url}: got status {resp.status}")
                return await resp.json(), resp
        except aiohttp.ContentTypeError as e:
            log.error(f"Aiohttp: invalid JSON response from {url}: {e}")
            raise AiohttpResponseException(f"Invalid JSON response from {url}") from e
        except Exception as e:
            log.exception(f"Aiohttp: unexpected error during get_json {url}")
            raise AiohttpClientException(f"Unexpected error during get_json {url}") from e

    async def post(self, url: str, data: dict, headers: dict = None):
        self._ensure_session()
        try:
            async with self._session.post(url=url, json=data, headers=headers) as resp:
                log.info(f"Aiohttp POST {url}: got status {resp.status}")
                return await resp.json()
        except ClientConnectionError as e:
            log.error(f"Aiohttp: connection error while POST {url}: {e}")
            raise AiohttpConnectionException(f"Connection error while POST {url}") from e
        except (TimeoutError, ServerTimeoutError) as e:
            log.error(f"Aiohttp: timeout while POST {url}")
            raise AiohttpTimeoutException(f"Timeout while POST {url}") from e
        except ClientResponseError as e:
            log.error(f"Aiohttp: bad response while POST {url}: {e}")
            raise AiohttpResponseException(f"Bad response while POST {url}: {e.status}") from e
        except ClientPayloadError as e:
            log.error(f"Aiohttp: payload error while POST {url}: {e}")
            raise AiohttpResponseException(f"Payload error while POST {url}") from e
        except Exception as e:
            log.exception(f"Aiohttp: unexpected error while POST {url}")
            raise AiohttpClientException(f"Unexpected error while POST {url}") from e
