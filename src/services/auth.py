from datetime import datetime, timezone, timedelta

import jwt
from passlib.context import CryptContext

from src.config import settings
from src.exceptions import InvalidCredentialsException, SignatureExpiredException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

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
