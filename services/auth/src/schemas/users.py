from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, AnyUrl

from src.schemas.base import BaseSchema, AtLeastOneFieldMixin
from src.schemas.pydatic_types import Str48, Date, PasswordStr, Str1024


class UserAddRequestDTO(BaseSchema):
    email: EmailStr
    password: PasswordStr
    first_name: Str48
    last_name: Str48 | None = None
    birth_date: Date | None = None
    bio: Str1024 | None = None


class UserAddDTO(BaseModel):
    id: UUID
    first_name: str
    last_name: str | None = None
    email: str
    birth_date: date | None = None
    bio: str | None = None
    picture: str | None = None
    provider_name: str | None = None
    password_hash: str | None = None
    is_active: bool | None = None


class UserDTO(BaseModel):
    id: UUID
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


class UserPatchRequestDTO(BaseSchema, AtLeastOneFieldMixin):
    first_name: Str48 | None = None
    last_name: Str48 | None = None
    birth_date: Date | None = None
    bio: Str1024 | None = None
    picture_url: AnyUrl | None = None


class UserPatchDTO(UserPatchRequestDTO):
    picture: str


class DBUserDTO(UserDTO):
    password_hash: str | None


class GoogleLoginDTO(BaseSchema):
    email: EmailStr


class UserLoginRequestDTO(GoogleLoginDTO):
    password: PasswordStr


class UserUpdateDTO(BaseModel):
    is_active: bool | None = None
    password_hash: str | None = None
