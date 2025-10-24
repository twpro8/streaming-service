import json
import logging
from secrets import token_urlsafe
from urllib.parse import urlencode

import jwt
from jwt import InvalidTokenError, PyJWK, PyJWKError

from src.adapters.aiohttp_client import AiohttpClient
from src.managers.redis import RedisManager
from src.exceptions import (
    GoogleOAuthClientException,
    NoIDTokenException,
    InvalidStateException,
    TokenVerificationException,
    JWKSFetchException,
)


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
        """Generate the Google OAuth redirect URL and store a temporary state in Redis."""
        try:
            state = token_urlsafe(16)
            await self.redis.set(state, "1", expire=120)
            log.debug(f"Google OAuth: state {state} stored in Redis.")
            return self._generate_google_oauth_redirect_uri(state)
        except Exception as e:
            log.exception("Google OAuth: Failed to generate redirect URI.")
            raise GoogleOAuthClientException("Failed to generate redirect URI.") from e

    async def exchange_code(self, code: str, state: str) -> dict:
        """Exchange an authorization code for an ID token and verify it."""
        await self._validate_state(state)
        try:
            response = await self.ac.post(
                url=self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            )
            id_token = response.get("id_token")
            if not id_token:
                log.error("Google OAuth: No ID token found in the response.")
                raise NoIDTokenException
            return await self._verify_token(id_token)
        except NoIDTokenException:
            raise
        except Exception as e:
            log.exception("Google OAuth: Failed to exchange code for token.")
            raise GoogleOAuthClientException("Failed to exchange code for token.") from e

    async def _validate_state(self, state: str) -> bool:
        """Validate the stored OAuth state token."""
        try:
            valid = await self.redis.getdel(state) is not None
            if not valid:
                log.warning(f"Google OAuth: Invalid or expired state '{state}'.")
            return valid
        except Exception as e:
            log.exception("Google OAuth: Failed to validate state.")
            raise InvalidStateException("Failed to validate state.") from e

    async def _verify_token(self, id_token: str) -> dict:
        """Verify the Google ID token using cached or fetched JWKS."""
        try:
            jwks = await self._get_cached_jwks()
            public_key = self._get_jwk_public_key(id_token, jwks)

            payload = jwt.decode(
                jwt=id_token,
                key=public_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer="https://accounts.google.com",
            )
            log.debug("Google OAuth: ID token successfully verified.")
            return payload
        except (InvalidTokenError, PyJWKError, ValueError) as e:
            log.error(f"Google OAuth: Invalid or malformed ID token: {e}")
            raise TokenVerificationException("Invalid or malformed ID token.") from e
        except Exception as e:
            log.exception("Google OAuth: Failed to verify ID token.")
            raise TokenVerificationException("Failed to verify Google ID token.") from e

    async def _get_cached_jwks(self) -> dict:
        """Get JWKS from Redis cache or fetch from Google if not cached."""
        try:
            jwks_raw = await self.redis.get("google_jwks")
            if jwks_raw:
                log.debug("Google OAuth: JWKS loaded from Redis cache.")
                return json.loads(jwks_raw)

            jwks, ttl = await self._fetch_jwks()
            await self.redis.set("google_jwks", json.dumps(jwks), expire=ttl)
            log.debug(f"Google OAuth: JWKS fetched and cached for {ttl} seconds.")
            return jwks
        except Exception as e:
            log.exception("Google OAuth: Failed to load JWKS.")
            raise JWKSFetchException("Failed to load or cache JWKS.") from e

    async def _fetch_jwks(self) -> tuple[dict, int]:
        """Fetch JWKS directly from Google's endpoint and determine cache TTL."""
        try:
            jwks, resp = await self.ac.get_json(url=self.jwks_url)
            cache_control = resp.headers.get("Cache-Control", "")
            ttl = 3600  # default: 1 hour
            if "max-age=" in cache_control:
                ttl = int(cache_control.split("max-age=")[1].split(",")[0])
            return jwks, ttl
        except Exception as e:
            log.exception("Google OAuth: Failed to fetch JWKS from Google.")
            raise JWKSFetchException("Failed to fetch JWKS from Google.") from e

    def _generate_google_oauth_redirect_uri(self, state: str) -> str:
        """Generate the OAuth2 authorization URL for Google sign-in."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
        }
        redirect_uri = f"{self.base_url}?{urlencode(params)}"
        log.debug(f"Google OAuth: Generated redirect URI {redirect_uri}")
        return redirect_uri

    @staticmethod
    def _get_jwk_public_key(id_token: str, jwks: dict):
        """Extract the public key from JWKS using the token's 'kid' header."""
        try:
            unverified_header = jwt.get_unverified_header(id_token)
            kid = unverified_header.get("kid")
            if not kid:
                raise ValueError("JWT header does not contain 'kid'.")

            key_data = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if not key_data:
                raise ValueError(f"Key with kid='{kid}' not found in JWKS.")

            return PyJWK(key_data).key
        except Exception as e:
            log.exception("Google OAuth: Failed to extract JWK public key.")
            raise TokenVerificationException("Failed to extract JWK public key.") from e
