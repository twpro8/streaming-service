import logging
from uuid import UUID

from uuid_extensions import uuid7

from src.config import settings
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
    ObjectNotFoundException,
    UserNotFoundException,
    IncorrectPasswordException,
    UserAlreadyExistsException,
    TokenRevokedException,
    ClientMismatchException,
    InvalidVerificationCodeException,
    UserAlreadyVerifiedException,
    SamePasswordException,
    UserUnverifiedException,
)
from src.schemas.auth import (
    RefreshTokenAddDTO,
    RefreshTokenUpdateDTO,
    EmailVerifyRequestDTO,
    PasswordChangeRequestDTO,
    PasswordResetRequestDTO,
)
from src.schemas.users import (
    UserAddDTO,
    UserAddRequestDTO,
    UserUpdateDTO,
    UserLoginRequestDTO,
    GoogleLoginDTO,
    UserDTO,
    DBUserDTO,
)
from src.services.utils import generate_upper_code, get_verification_key
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
        user_data: UserLoginRequestDTO | GoogleLoginDTO,
        info: ClientInfo,
    ) -> tuple[str, str]:
        try:
            user = await self.db.users.get_db_user(email=user_data.email)
        except UserNotFoundException:
            raise

        # login with password
        if isinstance(user_data, UserLoginRequestDTO):
            if not self.hasher.verify(user_data.password, user.password_hash):
                raise IncorrectPasswordException

            if not user.is_active:
                raise UserUnverifiedException

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

        # Email verification
        code = generate_upper_code()
        await self.redis.set(
            key=get_verification_key(user_data.email),
            value=code,
            expire=settings.USER_VERIFICATION_CODE_EXP,
        )
        send_verification_email.delay(
            to_email=user_data.email,
            code=code,
        )  # Sending an email as a background task

        await self.db.commit()
        log.debug("User %s registered successfully", user_data.email)

    async def verify_email(self, form_data: EmailVerifyRequestDTO):
        verification_key = get_verification_key(form_data.email)

        code = await self.redis.get(verification_key)
        if code is None or form_data.code != code:
            raise InvalidVerificationCodeException

        try:
            await self.db.users.update(
                data=UserUpdateDTO(is_active=True),
                email=form_data.email,
                exclude_unset=True,
            )
        except ObjectNotFoundException:
            raise UserNotFoundException

        await self.redis.delete(verification_key)
        await self.db.commit()

    async def resend_verification_code(self, email: str) -> None:
        user = await self.db.users.get_one_or_none(email=email)
        if not user:
            raise UserNotFoundException

        if user.is_active:
            raise UserAlreadyVerifiedException

        code = generate_upper_code()
        await self.redis.set(
            key=get_verification_key(email),
            value=code,
            expire=settings.USER_VERIFICATION_CODE_EXP,
        )
        send_verification_email.delay(email, code)

        log.debug(f"Auth Service: Verification code resent to {email}")

    async def forgot_password(self, email: str) -> None:
        user = await self.db.users.get_one_or_none(email=email)
        if not user:
            raise UserNotFoundException

        code = generate_upper_code()
        await self.redis.set(
            key=get_verification_key(user.email),
            value=code,
            expire=settings.PASSWORD_RESET_CODE_EXP,
        )
        send_verification_email.delay(user.email, code)

        log.debug(f"Auth Service: Verification code resent to {email}")

    async def reset_password(self, form_data: PasswordResetRequestDTO) -> None:
        verification_key = get_verification_key(form_data.email)

        code = await self.redis.get(verification_key)
        if code is None or form_data.code != code:
            raise InvalidVerificationCodeException

        password_hash = self.hasher.hash(form_data.new_password)
        try:
            await self.db.users.update(
                UserUpdateDTO(password_hash=password_hash),
                email=form_data.email,
                exclude_unset=True,
            )
        except ObjectNotFoundException:
            raise UserNotFoundException

        await self.redis.delete(verification_key)
        await self.db.commit()

        log.debug(f"Auth Service: Password reset. User email: {form_data.email}")

    async def change_password(self, user_id: UUID, form_data: PasswordChangeRequestDTO) -> None:
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

        log.debug(f"Auth Service: Password changed. User email: {user.email}")

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
            log.exception("Auth Service: State is invalid or expired")
            raise
        except NoIDTokenException:
            log.exception("Auth Service: No ID token received from Google")
            raise

        log.debug(f"Auth Service: Successfully got user data from Google: {user_data}")
        return await self._login_or_register_google_user(user_data, info)

    async def refresh_token(
        self,
        refresh_token_data: dict,
        info: ClientInfo,
    ) -> tuple[str, str]:
        old_token_id = refresh_token_data["jti"]
        user_id = refresh_token_data["sub"]

        db_token = await self.db.refresh_tokens.get_one_or_none(id=old_token_id)
        if not db_token:
            log.exception(f"Auth Service: Refresh token {old_token_id} not found")
            raise TokenRevokedException

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
            raise ClientMismatchException  # I recommend using fingerprint here instead

        # Token rotation: delete old and insert new
        await self.db.refresh_tokens.delete(id=old_token_id)
        new_access, new_refresh = await self._issue_tokens(user, info)

        await self.db.commit()

        log.debug(f"Auth Service: Refreshed tokens for user {user.email}")
        return new_access, new_refresh

    async def delete_refresh_token(self, token_data: dict) -> None:
        await self.db.refresh_tokens.delete(id=token_data["jti"])
        await self.db.commit()
        log.debug(f"Deleted refresh token {token_data['jti']}")

    async def _login_or_register_google_user(
        self,
        user_data: dict,
        info: ClientInfo,
    ) -> tuple[str, str]:
        """Attempting to log in via Google. If the user doesn't exist, we'll create one."""
        try:
            return await self.login(GoogleLoginDTO(email=user_data["email"]), info=info)
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

        return await self.login(GoogleLoginDTO(email=user_data["email"]), info=info)

    async def _issue_tokens(
        self,
        user: UserDTO | DBUserDTO,
        info: ClientInfo,
        token_id: UUID | None = None,
        update: bool = False,
    ) -> tuple[str, str]:
        if token_id is None:
            token_id = uuid7()

        _user_data = user.model_dump(
            mode="json",
            include={"id", "name", "email", "picture", "is_admin"},
        )
        access = self.jwt.create_access_token(_user_data)
        refresh, expire = self.jwt.create_refresh_token(
            {"sub": _user_data["id"], "jti": str(token_id)}
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
