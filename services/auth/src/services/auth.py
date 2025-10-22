import logging
from uuid import UUID

from pydantic import BaseModel
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
    IncorrectPasswordException,
    UserAlreadyExistsException,
    TokenRevokedException,
    ClientMismatchException,
)
from src.schemas.auth import RefreshTokenAddDTO, RefreshTokenUpdateDTO
from src.schemas.users import UserAddDTO, UserAddRequestDTO, UserDTO
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
        info: ClientInfo,
        email: str,
        password: str | None = None,
    ) -> tuple[str, str]:
        try:
            user = await self.db.users.get_db_user(email=email)
        except UserNotFoundException:
            raise

        if password and not self.hasher.verify(password, user.password_hash):
            raise IncorrectPasswordException

        existing_token = await self.db.refresh_tokens.get_one_or_none(
            user_id=user.id,
            ip=info.ip,
            user_agent=info.user_agent,
        )
        if existing_token:
            access_token, refresh_token = await self._issue_tokens(user, info, update=True)
        else:
            access_token, refresh_token = await self._issue_tokens(user, info)

        await self.db.commit()

        log.debug("User %s logged in successfully", user.email)
        return access_token, refresh_token

    async def register(self, data: UserAddRequestDTO | UserAddDTO) -> None:
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

        try:
            await self.db.users.add_user(data)
        except UserAlreadyExistsException:
            raise

        await self.db.commit()
        log.debug("User %s registered successfully", data.email)

    async def get_google_redirect_uri(self) -> str:
        return await self.google.get_redirect_uri()

    async def handle_google_callback(
        self,
        state: str,
        code: str,
        info: ClientInfo,
    ) -> tuple[str, str]:
        try:
            user_data = await self.google.exchange_code(code, state)
        except InvalidStateException:
            log.exception("State is invalid or expired")
            raise
        except NoIDTokenException:
            log.exception("No ID token received from Google")
            raise

        try:
            return await self.login(email=user_data["email"], info=info)
        except UserNotFoundException:
            pass

        try:
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
        except UserAlreadyExistsException:
            pass

        return await self.login(email=user_data["email"], info=info)

    async def refresh_token(
        self,
        refresh_token_data: dict,
        info: ClientInfo,
        user: UserDTO | None = None,
    ) -> tuple[str, str]:
        old_token_id = refresh_token_data["jti"]
        user_id = refresh_token_data["sub"]

        db_token = await self.db.refresh_tokens.get_one_or_none(id=old_token_id)
        if not db_token:
            log.exception("Refresh token %s not found", old_token_id)
            raise TokenRevokedException

        if not user:
            user = await self.db.users.get_one_or_none(id=user_id)
            if not user:
                raise UserNotFoundException

        if db_token.ip != info.ip or db_token.user_agent != info.user_agent:
            log.warning(
                "Client mismatch for token %s: expected %s/%s, got %s/%s",
                old_token_id,
                db_token.ip,
                db_token.user_agent,
                info.ip,
                info.user_agent,
            )
            raise ClientMismatchException

        # Token rotation: delete old and insert new
        await self.db.refresh_tokens.delete(id=old_token_id)
        new_access, new_refresh = await self._issue_tokens(user, info)

        await self.db.commit()

        log.debug("Refreshed tokens for user %s", user.email)
        return new_access, new_refresh

    async def delete_refresh_token(self, token_data: dict) -> None:
        await self.db.refresh_tokens.delete(id=token_data["jti"])
        await self.db.commit()
        log.debug("Deleted refresh token %s", token_data["jti"])

    async def _issue_tokens(
        self,
        user: BaseModel,
        info: ClientInfo,
        token_id: UUID | None = None,
        update: bool = False,
    ) ->  tuple[str, str]:
        if token_id is None:
            token_id = uuid7()

        refresh, expire = self.jwt.issue_refresh_token({"sub": str(user.id), "jti": str(token_id)})
        access = self.jwt.issue_access_token(user.model_dump(mode="json", exclude=("password_hash", "bio")))

        # If update=True, update the refresh token for the current device.
        if update:
            await self.db.refresh_tokens.update(
                data=RefreshTokenUpdateDTO(
                    id=token_id,
                    expires_at=expire,
                ),
                # filter
                user_id=user.id,
                ip=info.ip,
                user_agent=info.user_agent,
            )
        else:
            await self.db.refresh_tokens.add(
                RefreshTokenAddDTO(
                    id=token_id,
                    user_id=user.id,
                    ip=info.ip,
                    user_agent=info.user_agent,
                    expires_at=expire,
                ),
            )

        return access, refresh
