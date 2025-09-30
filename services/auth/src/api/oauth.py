import secrets

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.exceptions import InvalidStateHTTPException, NoIDTokenHTTPException
from src.google_oauth import generate_google_oauth_redirect_uri, verify_google_token
from src import redis_manager, aiohttp_client
from src.config import settings


v1_router = APIRouter(prefix="/v1/oauth", tags=["oauth"])


@v1_router.get("/google/uri")
async def get_google_oauth_redirect_uri():
    state = secrets.token_urlsafe(16)
    await redis_manager.set(state, "1", expire=300)
    uri = generate_google_oauth_redirect_uri(state)

    return RedirectResponse(url=uri, status_code=302)


@v1_router.get("/google")
async def google_callback(state: str, code: str):
    s = await redis_manager.get(state)
    if not s:
        raise InvalidStateHTTPException

    request_body = {
        "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
        "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.OAUTH_GOOGLE_REDIRECT_URL,
    }

    resp = await aiohttp_client.post(url=settings.GOOGLE_TOKEN_URL, data=request_body)

    id_token = resp.get("id_token")
    if not id_token:
        raise NoIDTokenHTTPException

    user_data = await verify_google_token(id_token, settings.OAUTH_GOOGLE_CLIENT_ID)

    return {"status": "ok", "user_data": user_data}
