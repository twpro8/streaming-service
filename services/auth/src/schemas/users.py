from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from src.schemas.base import BaseSchema


class UserAddRequestDTO(BaseSchema):
    email: EmailStr
    password: str
    first_name: str
    last_name: str | None = None
    birth_date: date | None = None
    bio: str | None = None

    @property
    def name(self):
        return self.first_name + " " + self.last_name if self.last_name else self.first_name

    @property
    def normalized_email(self) -> str:
        return str(self.email).strip().lower()


class UserAddDTO(BaseModel):
    id: UUID
    name: str
    first_name: str
    last_name: str | None = None
    email: str
    birth_date: date | None = None
    bio: str | None = None
    picture: str | None = None
    provider_name: str | None = None
    password_hash: str | None = None


class UserDTO(BaseModel):
    id: UUID
    name: str
    first_name: str
    last_name: str | None
    email: str
    birth_date: date | None
    bio: str | None
    picture: str | None
    provider_name: str | None
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DBUserDTO(UserDTO):
    password_hash: str | None


class UserLoginDTO(BaseSchema):
    email: str
    password: str
