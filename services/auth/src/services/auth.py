import hashlib
import json
import logging
import secrets
from datetime import datetime, timezone, timedelta
from uuid import UUID

import jwt
from jwt import PyJWKClient
from passlib.context import CryptContext
from uuid_extensions import uuid7

from src.config import settings
from src.exceptions import (
    InvalidCredentialsException,
    SignatureExpiredException,
    NoIDTokenException,
    InvalidStateException,
)
from src.google_oauth import generate_google_oauth_redirect_uri
from src.schemas.auth import RefreshTokenAddDTO
from src.schemas.users import UserAddDTO
from src.services.base import BaseService


log = logging.getLogger(__name__)


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            payload=to_encode,
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: UUID, token_id: UUID) -> tuple[str, str]:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = jwt.encode(
            payload={
                "sub": str(user_id),
                "jti": str(token_id),
                "exp": expire,
            },
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        return refresh_token, refresh_token_hash

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            data = jwt.decode(
                jwt=token,
                key=settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.exceptions.DecodeError:
            raise InvalidCredentialsException
        except jwt.exceptions.ExpiredSignatureError:
            raise SignatureExpiredException
        return data

    async def get_google_oauth_redirect_uri(self):
        state = secrets.token_urlsafe(16)
        await self.redis.set(state, "1", expire=60)
        url = generate_google_oauth_redirect_uri(state)

        return url

    async def handle_google_callback(self, state: str, code: str):
        s = await self.redis.get(state)
        if not s:
            raise InvalidStateException

        resp = await self.ac.post(
            url=settings.GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
                "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.OAUTH_GOOGLE_REDIRECT_URL,
            },
        )

        id_token = resp.get("id_token")
        if not id_token:
            raise NoIDTokenException

        user_data = await self.verify_google_token(id_token, settings.OAUTH_GOOGLE_CLIENT_ID)

        db_user = await self.db.users.get_one_or_none(email=user_data["email"])
        if db_user:
            access_token = self.create_access_token(data=db_user.model_dump(mode="json"))

            refresh_token_id = uuid7()
            refresh_token, refresh_token_hash = self.create_refresh_token(
                db_user.id, refresh_token_id
            )

            await self.db.refresh_tokens.add_one(
                RefreshTokenAddDTO(
                    id=refresh_token_id,
                    user_id=db_user.id,
                    token_hash=refresh_token_hash,
                )
            )
            await self.db.commit()

            return access_token, refresh_token

        user_id = uuid7()
        to_add = UserAddDTO(
            id=user_id,
            name=user_data["name"],
            first_name=user_data["given_name"],
            last_name=user_data.get("family_name"),
            email=user_data["email"],
            picture=user_data.get("picture"),
            provider_name="google",
        )

        new_user = await self.db.users.add_one(to_add)

        refresh_token_id = uuid7()
        refresh_token, refresh_token_hash = self.create_refresh_token(user_id, refresh_token_id)
        await self.db.refresh_tokens.add_one(
            RefreshTokenAddDTO(
                id=refresh_token_id,
                user_id=user_id,
                token_hash=refresh_token_hash,
            )
        )

        await self.db.commit()
        access_token = self.create_access_token(data=new_user.model_dump(mode="json"))

        return access_token, refresh_token

    async def fetch_google_jwks(self) -> tuple[dict, int]:
        jwks, resp = await self.ac.get_json(url=settings.GOOGLE_JWKS_URL)
        cache_control = resp.headers.get("Cache-Control", None)
        ttl = int(cache_control.split("max-age=")[1].split(",")[0])
        return jwks, ttl

    async def verify_google_token(self, id_token: str, client_id: str) -> dict:
        try:
            jwks_raw = await self.redis.get("google_jwks")
            if jwks_raw:
                jwks = json.loads(jwks_raw)
            else:
                jwks, ttl = await self.fetch_google_jwks()
                await self.redis.set("google_jwks", json.dumps(jwks), expire=ttl)

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
