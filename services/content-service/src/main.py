import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import uvicorn
from fastapi import FastAPI

from src.views import master_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    ...
    yield
    ...


app = FastAPI(lifespan=lifespan)
app.include_router(master_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
