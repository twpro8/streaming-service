from datetime import date

from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, uuid_pk, str_1024, str_256, str_48, created_at


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    name: Mapped[str_256]
    first_name: Mapped[str_48]
    last_name: Mapped[str_48]
    birth_date: Mapped[date | None]
    email: Mapped[str_256] = mapped_column(unique=True)
    hashed_password: Mapped[str_256 | None]
    bio: Mapped[str_1024 | None]
    picture: Mapped[str_256 | None]
    provider_name: Mapped[str_256 | None]
    created_at: Mapped[created_at]
    updated_at: Mapped[created_at]  # Make sure you have added the trigger to the migration.
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
