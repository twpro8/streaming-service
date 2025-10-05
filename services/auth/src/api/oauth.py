from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Query
from fastapi.responses import RedirectResponse

from src.api.dependencies import RedisManagerDep, GoogleOAuthClientDep
from src.exceptions import InvalidStateException, InvalidStateHTTPException
from src.factories.service import ServiceFactory
from src.services.auth import AuthService


v1_router = APIRouter(prefix="/v1/oauth", tags=["oauth"])


@v1_router.get("/google/uri")
async def get_google_oauth_redirect_uri(
    redis_manager: RedisManagerDep,
    google_oauth_client: GoogleOAuthClientDep,
):
    uri = await AuthService(
        redis=redis_manager,
        google=google_oauth_client,
    ).get_google_oauth_redirect_uri()
    return RedirectResponse(url=uri, status_code=302)


@v1_router.get("/google")
async def google_callback(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    state: str = Query(),
    code: str = Query(),
):
    try:
        tokens = await service.handle_google_callback(state, code)
    except InvalidStateException:
        raise InvalidStateHTTPException
    return {"status": "ok", "data": tokens}
