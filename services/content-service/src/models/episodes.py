from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import UUID as PG_UUID, ForeignKey, String, DateTime, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class EpisodeORM(Base):
    __tablename__ = "episodes"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    show_id: Mapped[UUID] = mapped_column(ForeignKey("shows.id", ondelete="CASCADE"))
    season_id: Mapped[UUID] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    episode_number: Mapped[int]
    duration: Mapped[int]
    video_url: Mapped[str | None] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )

    # Relationships
    show: Mapped["ShowORM"] = relationship()
    season: Mapped["SeasonORM"] = relationship(back_populates="episodes")

    __table_args__ = (
        UniqueConstraint("season_id", "episode_number", name="unique_episode_per_season"),
    )
