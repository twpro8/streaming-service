from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class FavoritesORM(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content_id: Mapped[int]
    content_type: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("TIMEZONE('UTC', now())")
    )

    __table_args__ = (
        UniqueConstraint("user_id", "content_id", "content_type", name="unique_favorite"),
    )
