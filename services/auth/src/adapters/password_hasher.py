from passlib.context import CryptContext
from src.exceptions import InvalidHashValueException


class PasswordHasher:
    def __init__(self, schemes: list[str], deprecated: str):
        self._context = CryptContext(schemes=schemes, deprecated=deprecated)

    def hash(self, value: str) -> str:
        return self._context.hash(value)

    def verify(self, plain_value: str, hashed_value: str) -> bool:
        try:
            return self._context.verify(plain_value, hashed_value)
        except Exception:
            raise InvalidHashValueException
