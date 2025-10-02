from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Query
from fastapi.responses import RedirectResponse, Response

from src.api.dependencies import RedisManagerDep
from src.exceptions import InvalidStateException, InvalidStateHTTPException
from src.factories.service import ServiceFactory
from src.services.auth import AuthService


v1_router = APIRouter(prefix="/v1/oauth", tags=["oauth"])


@v1_router.get("/google/uri")
async def get_google_oauth_redirect_uri(redis_manager: RedisManagerDep):
    uri = await AuthService(redis=redis_manager).get_google_oauth_redirect_uri()
    return RedirectResponse(url=uri, status_code=302)


@v1_router.get("/google")
async def google_callback(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    response: Response,
    state: str = Query(),
    code: str = Query(),
):
    try:
        access_token, refresh_token = await service.handle_google_callback(state, code)
    except InvalidStateException:
        raise InvalidStateHTTPException
    response.set_cookie(
        "access_token", access_token, httponly=True
    )  # use secure=True to ensure HTTPS
    return {"status": "ok", "access_token": access_token, "refresh_token": refresh_token}
