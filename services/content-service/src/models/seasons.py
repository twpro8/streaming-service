from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import UUID as PG_UUID, ForeignKey, String, DateTime, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class SeasonORM(Base):
    __tablename__ = "seasons"
    __table_args__ = (
        UniqueConstraint(
            "show_id",
            "season_number",
            name="uq_season",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    show_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("shows.id", ondelete="CASCADE"),
    )
    title: Mapped[str] = mapped_column(String(256))
    season_number: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )  # Make sure you have added the trigger to the migration.

    # Relationships
    show: Mapped["ShowORM"] = relationship(back_populates="seasons")
    episodes: Mapped[List["EpisodeORM"]] = relationship(back_populates="season")
