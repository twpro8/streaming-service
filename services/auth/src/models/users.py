from datetime import date

from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, uuid_pk, str_1024, str_256, str_128, str_48, created_at


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    name: Mapped[str_128]
    first_name: Mapped[str_48]
    last_name: Mapped[str_48 | None]
    email: Mapped[str_256] = mapped_column(unique=True)
    birth_date: Mapped[date | None]
    bio: Mapped[str_1024 | None]
    picture: Mapped[str_256 | None]
    password_hash: Mapped[str_256 | None]
    refresh_token_hash: Mapped[str_256 | None]
    provider_name: Mapped[str_48 | None]
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[created_at]  # Make sure you have added the trigger to the migration.
