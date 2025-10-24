import logging
from contextlib import asynccontextmanager
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import uvicorn
from fastapi import FastAPI

from src.api import master_router
from src.log_config import configure_logging
from src.api.dependencies import get_redis_manager, get_async_http_client


# Configuring the logging level and format
configure_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_manager = get_redis_manager()
    aiohttp_client = get_async_http_client()

    await redis_manager.connect()
    await aiohttp_client.startup()
    yield
    await redis_manager.close()
    await aiohttp_client.shutdown()


app = FastAPI(lifespan=lifespan, title="Auth Service")
app.include_router(master_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
