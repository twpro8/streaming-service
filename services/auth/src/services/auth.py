import logging
from uuid import UUID

from pydantic import BaseModel
from uuid_extensions import uuid7

from src.services.base import BaseService
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
    InvalidVerificationCodeException,
    UserAlreadyVerifiedException,
    TooManyRequestsException,
    SamePasswordException,
)
from src.schemas.auth import RefreshTokenAddDTO, RefreshTokenUpdateDTO, VerifyEmailRequestDTO, ChangePasswordRequestDTO, \
    ResetPasswordRequestDTO
from src.schemas.users import UserAddDTO, UserAddRequestDTO, UserDTO, UserUpdateDTO
from src.services.utils import generate_upper_code
from src.tasks.tasks import send_verification_email


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

    async def register(self, user_data: UserAddRequestDTO) -> None:
        password_hash = self.hasher.hash(user_data.password)

        user_data = UserAddDTO(
            id=uuid7(),
            email=user_data.normalized_email,
            password_hash=password_hash,
            name=user_data.name,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            birth_date=user_data.birth_date,
            bio=user_data.bio,
            is_active=False,
        )

        try:
            await self.db.users.add_user(user_data)
        except UserAlreadyExistsException:
            raise

        await self.db.commit()

        # Email verification
        code = generate_upper_code()
        await self.redis.set(code, user_data.email, expire=600)
        send_verification_email.delay(
            user_data.email, code
        )  # Sending an email as a background task

        log.debug("User %s registered successfully", user_data.email)

    async def verify_email(self, form_data: VerifyEmailRequestDTO):
        email = await self.redis.getdel(form_data.code)
        if email is None or form_data.email != email:
            raise InvalidVerificationCodeException

        user = await self.db.users.get_db_user(email=form_data.email)
        if not user:
            raise UserNotFoundException

        await self.db.users.update(
            data=UserUpdateDTO(is_active=True),
            email=form_data.email,
            exclude_unset=True,
        )
        await self.db.commit()

    async def resend_verification_code(self, email: str) -> None:
        # checking rate limit
        rate_limit_key = f"verify-rate-limit:{email}"
        if await self.redis.get(rate_limit_key):
            raise TooManyRequestsException

        user = await self.db.users.get_one_or_none(email=email)
        if not user:
            raise UserNotFoundException

        if user.is_active:
            raise UserAlreadyVerifiedException

        # setting rate limit
        await self.redis.set(rate_limit_key, "1", expire=60)

        code = generate_upper_code()
        await self.redis.set(code, user.email, expire=600)
        send_verification_email.delay(user.email, code)

        log.debug("Verification code resent to %s", user.email)

    async def forgot_password(self, email: str) -> None:
        # checking rate limit
        rate_limit_key = f"reset-rate-limit:{email}"
        if await self.redis.get(rate_limit_key):
            raise TooManyRequestsException

        user = await self.db.users.get_one_or_none(email=email)
        if not user:
            raise UserNotFoundException

        # setting rate limit
        await self.redis.set(rate_limit_key, "1", expire=60)

        code = generate_upper_code()
        await self.redis.set(code, user.email, expire=600)
        send_verification_email.delay(user.email, code)

    async def reset_password(self, form_data: ResetPasswordRequestDTO) -> None:
        email = await self.redis.getdel(form_data.code)
        if not email:
            raise InvalidVerificationCodeException

        user = await self.db.users.get_db_user(email=email)
        if not user:
            raise UserNotFoundException

        if self.hasher.verify(form_data.new_password, user.password_hash):
            raise SamePasswordException

        password_hash = self.hasher.hash(form_data.new_password)
        await self.db.users.update(
            UserUpdateDTO(password_hash=password_hash),
            email=email,
            exclude_unset=True,
        )
        await self.db.commit()

    async def change_password(self, user_id: UUID, form_data: ChangePasswordRequestDTO) -> None:
        user = await self.db.users.get_db_user(id=user_id)

        if not self.hasher.verify(form_data.password, user.password_hash):
            raise IncorrectPasswordException

        if self.hasher.verify(form_data.new_password, user.password_hash):
            raise SamePasswordException

        password_hash = self.hasher.hash(form_data.new_password)
        await self.db.users.update(
            UserUpdateDTO(password_hash=password_hash),
            id=user_id,
            exclude_unset=True,
        )
        await self.db.commit()

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
            await self.db.users.add_user(
                UserAddDTO(
                    id=uuid7(),
                    email=user_data["email"],
                    name=user_data["name"],
                    first_name=user_data["given_name"],
                    last_name=user_data.get("family_name"),
                    provider_name="google",
                    picture=user_data.get("picture"),
                    is_active=True,
                )
            )
        except UserAlreadyExistsException:
            pass

        await self.db.commit()

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
    ) -> tuple[str, str]:
        if token_id is None:
            token_id = uuid7()

        refresh, expire = self.jwt.issue_refresh_token({"sub": str(user.id), "jti": str(token_id)})
        access = self.jwt.issue_access_token(
            user.model_dump(mode="json", exclude=("password_hash", "bio"))
        )

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
