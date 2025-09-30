import json
import logging
from urllib.parse import urlencode

import jwt
from jwt import PyJWKClient

from src import redis_manager, aiohttp_client
from src.config import settings


log = logging.getLogger(__name__)


def generate_google_oauth_redirect_uri(state: str):
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
        "redirect_uri": settings.OAUTH_GOOGLE_REDIRECT_URL,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
    }
    return f"{base_url}?{urlencode(params)}"


async def fetch_google_jwks() -> tuple[dict, int]:
        jwks, resp = await aiohttp_client.get_json(url=settings.GOOGLE_JWKS_URL)
        cache_control = resp.headers.get("Cache-Control", None)
        ttl = int(cache_control.split("max-age=")[1].split(",")[0])
        return jwks, ttl


async def verify_google_token(id_token: str, client_id: str) -> dict:
    try:
        jwks_raw = await redis_manager.get("google_jwks")
        if jwks_raw:
            jwks = json.loads(jwks_raw)
        else:
            jwks, ttl = await fetch_google_jwks()
            await redis_manager.set("google_jwks", json.dumps(jwks), expire=ttl)

        jwks_client = PyJWKClient(settings.GOOGLE_JWKS_URL, cache_keys=jwks)
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)

        payload = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
            issuer="https://accounts.google.com",
        )
    except Exception as e:
        log.error(f"Failed to verify Google ID token: {e}")
        raise
    return payload
