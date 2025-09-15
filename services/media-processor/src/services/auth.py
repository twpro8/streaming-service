import jwt

from src.config import settings
from src.exceptions import InvalidCredentialsException, SignatureExpiredException


class AuthService:
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
