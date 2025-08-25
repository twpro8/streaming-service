# ruff: noqa
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base


class CommentORM(Base):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[int]
    movie_id: Mapped[UUID] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), nullable=True
    )
    show_id: Mapped[UUID] = mapped_column(ForeignKey("shows.id", ondelete="CASCADE"), nullable=True)
    comment: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("TIMEZONE('UTC', now())")
    )

    # Relationships
    movie: Mapped["MovieORM"] = relationship(back_populates="comments")
    show: Mapped["ShowORM"] = relationship(back_populates="comments")
