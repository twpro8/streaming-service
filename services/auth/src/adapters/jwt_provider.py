from datetime import datetime, timezone, timedelta

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError

from src.exceptions import InvalidCredentialsException, SignatureExpiredException


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

    def create_access_token(self, data: dict) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_expire_minutes)
        return jwt.encode({**data, "exp": expire}, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_expire_days)
        return jwt.encode({**data, "exp": expire}, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except ExpiredSignatureError:
            raise SignatureExpiredException
        except InvalidTokenError:
            raise InvalidCredentialsException
        return payload
