import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
import uvicorn

from src.core.router import master_router
from src import redis_manager


async def lifespan(app: FastAPI):
    await redis_manager.connect()
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)
app.include_router(master_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
