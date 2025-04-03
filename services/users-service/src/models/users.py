from datetime import datetime
from typing import List

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    DateTime,
    text,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class FriendshipORM(Base):
    __tablename__ = "friendships"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    friend_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("TIMEZONE('UTC', now())")
    )

    __table_args__ = (
        UniqueConstraint("user_id", "friend_id", name="uq_friendship"),
        CheckConstraint("user_id != friend_id", name="check_not_self_friend"),
    )

    def __repr__(self):
        return f"<Friendship(user_id={self.user_id}, friend_id={self.friend_id})>"


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
        secondary="friendships",
        primaryjoin=id == FriendshipORM.user_id,
        secondaryjoin=id == FriendshipORM.friend_id,
        backref="friends_reverse",
    )
