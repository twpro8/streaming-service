from datetime import datetime
from typing import List

from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


user_friend_association = Table(
    "users_friends_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("friend_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str | None] = mapped_column(String(255), default=None)
    bio: Mapped[str | None] = mapped_column(String(512), default=None)
    avatar: Mapped[str | None] = mapped_column(String(512), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("TIMEZONE('UTC', now())")
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    friends: Mapped[List["UserORM"]] = relationship(
        secondary=user_friend_association,
        primaryjoin=id == user_friend_association.c.user_id,
        secondaryjoin=id == user_friend_association.c.friend_id,
        backref="friend_of",
    )
