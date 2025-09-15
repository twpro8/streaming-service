from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr

from src.schemas.base import BaseSchema
from src.schemas.pydatic_types import email_str, password_str, IDInt


class UserDTO(BaseModel):
    id: IDInt
    email: EmailStr | None
    name: str
    bio: str | None
    avatar: str | None
    provider: str | None
    provider_id: IDInt | None
    created_at: datetime
    is_admin: bool
    is_active: bool


class UserAddRequestDTO(BaseSchema):
    email: email_str
    name: str
    password: password_str


class UserAddDTO(BaseModel):
    email: email_str
    name: str
    hashed_password: str


class UserLoginRequestDTO(BaseSchema):
    email: email_str
    password: password_str


class UserLoginDTO(BaseSchema):
    email: email_str
    password: password_str


class DBUserDTO(UserDTO):
    hashed_password: str


class UserAddGoogleDTO(BaseModel):
    email: email_str
    name: str
    avatar: str
    provider: str
    provider_id: IDInt


class UserAddGitHubDTO(BaseModel):
    name: str
    avatar: str
    provider: str
    provider_id: IDInt


class UserWithFavoritesDTO(UserDTO):
    favorites_ids: List[int]
