import uvicorn
from fastapi import FastAPI

from src.views import master_router


app = FastAPI()
app.include_router(master_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
