from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.api.dependencies import DBDep
from src import redis_manager, aiohttp_client
from src.services.auth import AuthService


v1_router = APIRouter(prefix="/v1/oauth", tags=["oauth"])


@v1_router.get("/google/uri")
async def get_google_oauth_redirect_uri():
    uri = await AuthService(redis=redis_manager).get_google_oauth_redirect_uri()
    return RedirectResponse(url=uri, status_code=302)


@v1_router.get("/google")
async def google_callback(db: DBDep, state: str, code: str):
    user = await AuthService(
        db=db,
        redis=redis_manager,
        ac=aiohttp_client,
    ).handle_google_callback(state, code)
    return {"status": "ok", "data": {"user": user}}
