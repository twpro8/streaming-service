import json
import logging
from secrets import token_urlsafe
from urllib.parse import urlencode

import jwt

from src.adapters.aiohttp_client import AiohttpClient
from src.managers.redis import RedisManager


log = logging.getLogger(__name__)


class GoogleOAuthClient:
    def __init__(
        self,
        ac: AiohttpClient,
        redis: RedisManager,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        token_url: str,
        jwks_url: str,
        base_url: str,
    ):
        self.ac = ac
        self.redis = redis
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_url = token_url
        self.jwks_url = jwks_url
        self.base_url = base_url

    async def get_redirect_uri(self) -> str:
        state = token_urlsafe(16)
        await self.redis.set(state, "1", expire=120)
        return self._generate_google_oauth_redirect_uri(state)

    async def exchange_code(self, code: str):
        resp = await self.ac.post(
            url=self.token_url,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            },
        )
        return resp

    async def verify_token(self, id_token: str) -> dict:
        try:
            jwks = await self._get_cached_jwks()
            p_key = self._get_jwk_public_key(id_token, jwks)

            payload = jwt.decode(
                jwt=id_token,
                key=p_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer="https://accounts.google.com",
            )

            return payload

        except Exception as e:
            log.error(f"Failed to verify Google ID token: {e}")
            raise

    async def validate_state(self, state: str) -> bool:
        return await self.redis.get(state) is not None

    async def _get_cached_jwks(self) -> dict:
        jwks_raw = await self.redis.get("google_jwks")
        if jwks_raw:
            return json.loads(jwks_raw)

        jwks, ttl = await self._fetch_jwks()
        await self.redis.set("google_jwks", json.dumps(jwks), expire=ttl)

        return jwks

    async def _fetch_jwks(self) -> tuple[dict, int]:
        jwks, resp = await self.ac.get_json(url=self.jwks_url)
        cache_control = resp.headers.get("Cache-Control", None)
        ttl = 3600  # 1 hour by default
        if "max-age=" in cache_control:
            ttl = int(cache_control.split("max-age=")[1].split(",")[0])
        return jwks, ttl

    def _generate_google_oauth_redirect_uri(self, state: str):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
        }
        return f"{self.base_url}?{urlencode(params)}"

    @staticmethod
    def _get_jwk_public_key(id_token: str, jwks: dict):
        unverified_header = jwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")
        if not kid:
            raise ValueError("JWT does not contain kid in header.")

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise ValueError(f"Key with kid={kid} not found in JWKS.")

        jwk_obj = jwt.PyJWK(key)

        return jwk_obj.key
