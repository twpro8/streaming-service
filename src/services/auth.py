from datetime import datetime, timezone, timedelta

import jwt
from fastapi import Request
from authlib.integrations.starlette_client import OAuth
from passlib.context import CryptContext
from pydantic import BaseModel

from src.config import settings
from src.exceptions import (
    InvalidCredentialsException,
    SignatureExpiredException,
    UserNotFoundException,
    IncorrectPasswordException,
)
from src.schemas.users import UserAddGoogleDTO, UserAddDTO
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth = OAuth()
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        authorize_params=None,
        access_token_url="https://oauth2.googleapis.com/token",
        access_token_params=None,
        refresh_token_url=None,
        client_kwargs={
            "scope": "openid email profile",
            "redirect_uri": settings.GOOGLE_REDIRECT_URL,
        },
    )

    @classmethod
    async def get_google_login_url(cls, request: Request):
        request.session.clear()
        request.headers.get("referer")
        request.session["login_redirect"] = settings.FRONTEND_URL
        return await cls.oauth.google.authorize_redirect(
            request, settings.GOOGLE_REDIRECT_URL, prompt="consent"
        )

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
            to_encode, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            data = jwt.decode(
                token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.exceptions.DecodeError:
            raise InvalidCredentialsException
        except jwt.exceptions.ExpiredSignatureError:
            raise SignatureExpiredException
        return data

    async def register_user(self, user_data: BaseModel):
        normalized_email = user_data.email.strip().lower()
        hashed_password = AuthService.get_password_hash(password=user_data.password)

        new_user_data = UserAddDTO(
            name=user_data.name, email=normalized_email, hashed_password=hashed_password
        )

        user = await self.db.users.add_one(new_user_data)
        await self.db.commit()
        return user

    async def login_with_password(self, user_data: BaseModel):
        user = await self.db.users.get_db_user(email=user_data.email)
        if not user:
            raise UserNotFoundException
        if not AuthService.verify_password(user_data.password, user.hashed_password):
            raise IncorrectPasswordException
        access_token = AuthService.create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "bio": user.bio,
                "avatar": user.avatar,
                "provider": user.provider,
                "created_at": str(user.created_at),
            }
        )
        return access_token

    async def handle_google_callback(self, request: Request) -> str:
        """Login or register user"""
        token = await self.oauth.google.authorize_access_token(request)
        user_info = await self.oauth.google.get(
            "https://www.googleapis.com/oauth2/v3/userinfo", token=token
        )
        user_info_json = user_info.json()

        user = await self.db.users.get_one_or_none(email=user_info_json["email"])
        if user is None:
            user_to_add = UserAddGoogleDTO(
                email=user_info_json["email"],
                name=user_info_json["name"],
                avatar=user_info_json["picture"],
                provider="google",
            )
            user = await self.db.users.add_one(user_to_add)

        access_token = self.create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "bio": user.bio,
                "avatar": user.avatar,
                "provider": user.provider,
                "created_at": str(user.created_at),
            }
        )

        await self.db.commit()
        return access_token
