from typing import List

from datetime import datetime

from sqlalchemy import String, ForeignKey, UniqueConstraint, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class PlaylistORM(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("TIMEZONE('UTC', now())")
    )

    __table_args__ = (UniqueConstraint("user_id", "name", name="unique_playlist"),)

    # Relationships
    items: Mapped[List["PlaylistItemORM"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan"
    )


class PlaylistItemORM(Base):
    __tablename__ = "playlist_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id", ondelete="CASCADE"))
    content_id: Mapped[int]  # Polymorphic ID: can refer to film or series
    content_type: Mapped[str] = mapped_column(String(50))  # Example: "film" or "series"
    added_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("TIMEZONE('UTC', now())")
    )

    __table_args__ = (
        UniqueConstraint("playlist_id", "content_id", "content_type", name="unique_playlist_item"),
    )

    # Relationships
    playlist: Mapped["PlaylistORM"] = relationship(back_populates="items")
