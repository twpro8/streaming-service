import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src import rabbitmq_manager
from src.config import settings
from src.views import master_router
from src.middleware import MetricsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq_manager.connect()
    yield
    await rabbitmq_manager.connect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.FASTAPI_SECRET_KEY)
app.add_middleware(MetricsMiddleware)
app.include_router(master_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
