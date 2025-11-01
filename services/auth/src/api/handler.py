from fastapi import Request
from fastapi.responses import JSONResponse


async def app_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
