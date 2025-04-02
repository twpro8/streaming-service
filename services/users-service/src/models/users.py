from datetime import datetime
from typing import List

from sqlalchemy import String, Boolean, ForeignKey, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class UserFriendORM(Base):
    __tablename__ = "users_friends_association"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    friend_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    user: Mapped["UserORM"] = relationship(backref="friends_association")
    friend: Mapped["UserORM"] = relationship()


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str | None] = mapped_column(String(255), default=None)
    bio: Mapped[str | None] = mapped_column(String(512), default=None)
    avatar: Mapped[str | None] = mapped_column(String(512), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("TIMEZONE('UTC', now())")
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    friends: Mapped[List["UserORM"]] = relationship(
        secondary="users_friends_association",
        primaryjoin=id == UserFriendORM.user_id,
        secondaryjoin=id == UserFriendORM.friend_id,
        backref="friends_reverse",
    )
