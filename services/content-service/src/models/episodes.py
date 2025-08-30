from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import UUID as PG_UUID, ForeignKey, String, DateTime, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class EpisodeORM(Base):
    __tablename__ = "episodes"
    __table_args__ = (
        UniqueConstraint(
            "season_id",
            "episode_number",
            name="uq_episode",
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
    season_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
    )
    title: Mapped[str] = mapped_column(String(256))
    episode_number: Mapped[int]
    duration: Mapped[int | None]
    video_url: Mapped[str | None] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )  # Make sure you have added the trigger to the migration.

    # Relationships
    show: Mapped["ShowORM"] = relationship()
    season: Mapped["SeasonORM"] = relationship(back_populates="episodes")
