import logging

from uuid_extensions import uuid7

from src.adapters.jwt_provider import JwtProvider
from src.adapters.password_hasher import PasswordHasher
from src.adapters.google_client import GoogleOAuthClient
from src.adapters.aiohttp_client import AiohttpClient
from src.api.dependencies import ClientInfo
from src.managers.db import DBManager
from src.managers.redis import RedisManager
from src.exceptions import (
    NoIDTokenException,
    InvalidStateException,
    UserNotFoundException,
    InvalidHashValueException,
    IncorrectPasswordException, RefreshTokenNotFoundException,
)
from src.schemas.auth import RefreshTokenAddDTO
from src.schemas.users import UserAddDTO, UserAddRequestDTO
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

    async def login(
        self,
        email: str,
        client_info: ClientInfo,
        password: str | None = None,
    ) -> tuple[str, str]:
        try:
            user = await self.db.users.get_db_user(email=email)
        except UserNotFoundException:
            raise

        if password:
            try:
                self.hasher.verify(password, user.password_hash)
            except InvalidHashValueException:
                raise IncorrectPasswordException

        token_id = uuid7()
        access_token = self.jwt.create_access_token(
            data=user.model_dump(mode="json", exclude=["password_hash"]),
        )
        refresh_token, expire = self.jwt.create_refresh_token(
            {
                "sub": str(user.id),
                "jti": str(token_id),
            },
        )
        await self.db.refresh_tokens.add(
            RefreshTokenAddDTO(
                id=token_id,
                user_id=user.id,
                ip=client_info.ip,
                user_agent=client_info.user_agent,
                expires_at=expire,
            ),
        )
        await self.db.commit()

        return access_token, refresh_token

    async def register(self, data: UserAddRequestDTO | UserAddDTO):
        if isinstance(data, UserAddRequestDTO):
            user_id = uuid7()
            password_hash = self.hasher.hash(data.password)

            data = UserAddDTO(
                id=user_id,
                email=data.normalized_email,
                password_hash=password_hash,
                name=data.name,
                first_name=data.first_name,
                last_name=data.last_name,
                birth_date=data.birth_date,
                bio=data.bio,
            )

        await self.db.users.add(data)
        await self.db.commit()

    async def get_google_redirect_uri(self):
        return await self.google.get_redirect_uri()

    async def handle_google_callback(self, state: str, code: str, client_info: ClientInfo):
        try:
            await self.google.validate_state(state)
        except InvalidStateException:
            raise

        try:
            user_data = await self.google.exchange_code(code)
        except NoIDTokenException:
            log.exception("No ID token received from Google")
            raise

        try:
            return await self.login(email=user_data["email"], client_info=client_info)
        except UserNotFoundException:
            pass

        await self.register(
            UserAddDTO(
                id=uuid7(),
                email=user_data["email"],
                name=user_data["name"],
                first_name=user_data["given_name"],
                last_name=user_data.get("family_name"),
                provider_name="google",
                picture=user_data.get("picture"),
            )
        )

        return await self.login(email=user_data["email"], client_info=client_info)

    async def refresh_token(self, refresh_token_data: dict, client: ClientInfo):
        token_id = refresh_token_data.get("jti")
        user_id = refresh_token_data["sub"]

        token = await self.db.refresh_tokens.get_one_or_none(id=token_id)
        if not token:
            raise RefreshTokenNotFoundException

        user = await self.db.users.get_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundException

        new_access = self.jwt.create_access_token(user.model_dump(mode="json"))
        new_token_id = uuid7()
        new_refresh, expire = self.jwt.create_refresh_token(
            {
                "sub": str(user.id),
                "jti": str(new_token_id),
            }
        )

        # Token rotation: delete old and insert new
        await self.db.refresh_tokens.delete(id=token_id)
        await self.db.refresh_tokens.add(
            RefreshTokenAddDTO(
                id=new_token_id,
                user_id=user.id,
                ip=client.ip,
                user_agent=client.user_agent,
                expires_at=expire,
            ),
        )

        await self.db.commit()

        return new_access, new_refresh

    async def delete_refresh_token(self, token_data: dict):
        await self.db.refresh_tokens.delete(id=token_data["jti"])
        await self.db.commit()
