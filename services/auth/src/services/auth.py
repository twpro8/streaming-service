import logging

from uuid_extensions import uuid7

from src.adapters.jwt_provider import JwtProvider
from src.adapters.password_hasher import PasswordHasher
from src.adapters.google_client import GoogleOAuthClient
from src.adapters.aiohttp_client import AiohttpClient
from src.managers.db import DBManager
from src.managers.redis import RedisManager
from src.exceptions import (
    InvalidCredentialsException,
    SignatureExpiredException,
    NoIDTokenException,
    InvalidStateException,
    UserNotFoundException,
    InvalidRefreshTokenException,
    RefreshTokenNotFoundException,
    InvalidHashValueException,
)
from src.schemas.auth import RefreshTokenAddDTO, TokenDTO
from src.schemas.users import UserAddDTO
from src.services.base import BaseService


log = logging.getLogger(__name__)


class AuthService(BaseService):
    redis: RedisManager | None
    ac: AiohttpClient | None
    jwt: JwtProvider | None
    hasher: PasswordHasher | None
    google: GoogleOAuthClient | None

    def __init__(
        self,
        db: DBManager | None = None,
        redis: RedisManager | None = None,
        ac: AiohttpClient | None = None,
        jwt: JwtProvider | None = None,
        hasher: PasswordHasher | None = None,
        google: GoogleOAuthClient | None = None,
    ):
        super().__init__(db=db)
        self.redis = redis
        self.ac = ac
        self.jwt = jwt
        self.hasher = hasher
        self.google = google

    async def get_google_oauth_redirect_uri(self):
        return await self.google.get_redirect_uri()

    async def handle_google_callback(self, state: str, code: str):
        if not await self.google.validate_state(state):
            raise InvalidStateException

        id_token = (await self.google.exchange_code(code)).get("id_token")
        if not id_token:
            raise NoIDTokenException
        user_data = await self.google.verify_token(id_token)

        db_user = await self.db.users.get_one_or_none(email=user_data["email"])
        if db_user:
            access_token = self.jwt.create_access_token(data=db_user.model_dump(mode="json"))

            refresh_token_id = uuid7()
            refresh_token = self.jwt.create_refresh_token(
                {
                    "sub": str(db_user.id),
                    "jti": str(refresh_token_id),
                }
            )

            await self.db.refresh_tokens.add_one(
                RefreshTokenAddDTO(
                    id=refresh_token_id,
                    user_id=db_user.id,
                    token_hash=self.hasher.hash(refresh_token),
                )
            )
            await self.db.commit()

            return TokenDTO(access=access_token, refresh=refresh_token)

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
        refresh_token = self.jwt.create_refresh_token(
            {
                "sub": str(db_user.id),
                "jti": str(refresh_token_id),
            }
        )
        await self.db.refresh_tokens.add_one(
            RefreshTokenAddDTO(
                id=refresh_token_id,
                user_id=user_id,
                token_hash=self.hasher.hash(refresh_token),
            )
        )

        await self.db.commit()
        access_token = self.jwt.create_access_token(data=new_user.model_dump(mode="json"))

        return TokenDTO(access=access_token, refresh=refresh_token)

    async def refresh_token(self, refresh_token: str):
        try:
            payload = self.jwt.decode_token(refresh_token)
            old_token_id = payload.get("jti")
        except (InvalidCredentialsException, SignatureExpiredException):
            raise InvalidRefreshTokenException

        token_in_db = await self.db.refresh_tokens.get_one_or_none(id=old_token_id)
        if not token_in_db:
            raise RefreshTokenNotFoundException

        try:
            self.hasher.verify(refresh_token, token_in_db.token_hash)
        except InvalidHashValueException:
            raise InvalidRefreshTokenException

        user = await self.db.users.get_one_or_none(id=payload["sub"])
        if not user:
            raise UserNotFoundException

        new_access = self.jwt.create_access_token(user.model_dump(mode="json"))
        new_token_id = uuid7()
        new_refresh = self.jwt.create_refresh_token(
            {
                "sub": str(user.id),
                "jti": str(new_token_id),
            }
        )

        # Token rotation: delete old and insert new
        await self.db.refresh_tokens.delete(id=old_token_id)
        await self.db.refresh_tokens.add_one(
            RefreshTokenAddDTO(
                id=new_token_id,
                user_id=user.id,
                token_hash=self.hasher.hash(str(new_token_id)),
            ),
        )

        await self.db.commit()

        return TokenDTO(access=new_access, refresh=new_refresh)

    async def revoke_refresh_token(self, refresh_token: str):
        try:
            payload = self.jwt.decode_token(refresh_token)
            token_id = payload.get("jti")
        except (InvalidCredentialsException, SignatureExpiredException):
            raise InvalidRefreshTokenException

        token_in_db = await self.db.refresh_tokens.get_one_or_none(id=token_id)
        if not token_in_db:
            raise RefreshTokenNotFoundException

        try:
            self.hasher.verify(refresh_token, token_in_db.token_hash)
        except InvalidHashValueException:
            raise InvalidRefreshTokenException

        await self.db.refresh_tokens.delete(id=token_id)
        await self.db.commit()
