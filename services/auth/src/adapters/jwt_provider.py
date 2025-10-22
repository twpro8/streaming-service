import logging
from datetime import datetime, timezone, timedelta

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from src.exceptions import (
    InvalidCredentialsException,
    SignatureExpiredException,
    JWTProviderException,
)


log = logging.getLogger(__name__)


class JwtProvider:
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_expire_minutes: int,
        refresh_expire_days: int,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire_minutes = access_expire_minutes
        self.refresh_expire_days = refresh_expire_days

    def issue_access_token(self, data: dict) -> str:
        """Generate a short-lived access token."""
        try:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_expire_minutes)
            payload = {**data, "exp": expire}
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            log.debug("JWT: Access token created successfully.")
            return token
        except Exception as e:
            log.exception("JWT: Failed to create access token.")
            raise JWTProviderException("Failed to create access token.") from e

    def issue_refresh_token(self, data: dict) -> tuple[str, datetime]:
        """Generate a long-lived refresh token."""
        try:
            expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_expire_days)
            payload = {**data, "exp": expire}
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            log.debug("JWT: Refresh token created successfully.")
            return token, expire
        except Exception as e:
            log.exception(f"JWT: Failed to create refresh token. {e}")
            raise JWTProviderException("Failed to create refresh token.") from e

    def decode_token(self, token: str) -> dict:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            log.debug("JWT: Token decoded successfully.")
            return payload
        except ExpiredSignatureError as e:
            log.warning("JWT: Token has expired.")
            raise SignatureExpiredException from e
        except InvalidTokenError as e:
            log.warning("JWT: Invalid token provided.")
            raise InvalidCredentialsException from e
        except Exception as e:
            log.exception("JWT: Unexpected error during token decoding.")
            raise JWTProviderException("Unexpected error while decoding token.") from e
