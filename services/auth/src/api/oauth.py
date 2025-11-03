from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Query
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, Response

from src.api.dependencies import (
    RedisManagerDep,
    GoogleOAuthClientDep,
    ClientInfoDep,
    PreventDuplicateLoginDep,
    get_oauth_code_verifier,
    verify_oauth_state,
    create_oauth_state,
    create_pkce_pair,
)
from src.factories.service import ServiceFactory
from src.services.auth import AuthService


v1_router = APIRouter(prefix="/v1/oauth", tags=["OAuth"])


@v1_router.get("/google/uri", dependencies=[PreventDuplicateLoginDep])
async def get_google_oauth_redirect_uri(
    request: Request,
    state: Annotated[str, Depends(create_oauth_state)],
    pkce_pair: Annotated[tuple[str, str], Depends(create_pkce_pair)],
    redis_manager: RedisManagerDep,
    google_oauth_client: GoogleOAuthClientDep,
):
    code_verifier, code_challenge = pkce_pair

    uri = await AuthService(
        redis=redis_manager,
        google=google_oauth_client,
    ).get_google_redirect_uri(state, code_challenge)

    # Store state & code_verifier in the user's session (server-side)
    # Use session storage bound to the user (cookie-based session stored on server or encrypted cookie).
    request.session["oauth_state"] = state
    request.session["oauth_code_verifier"] = code_verifier

    return RedirectResponse(url=uri, status_code=302)


@v1_router.get(
    "/google",
    dependencies=[
        PreventDuplicateLoginDep,
        Depends(verify_oauth_state),
    ],
)
async def google_callback(
    code_verifier: Annotated[str, Depends(get_oauth_code_verifier)],
    client_info: ClientInfoDep,
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    response: Response,
    code: str = Query(),
):
    access, refresh = await service.handle_google_callback(
        code=code,
        code_verifier=code_verifier,
        info=client_info,
    )
    response.set_cookie("access_token", access, httponly=True)
    response.set_cookie("refresh_token", refresh, httponly=True)  # Add path here
    return {"status": "ok"}
