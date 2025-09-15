from uuid import UUID

from sqlalchemy import UUID as PG_UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk, created_at, str_256


class EpisodeORM(Base):
    __tablename__ = "episodes"
    __table_args__ = (
        UniqueConstraint(
            "season_id",
            "episode_number",
            name="uq_episode",
        ),
    )

    id: Mapped[uuid_pk]
    show_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("shows.id", ondelete="CASCADE"),
    )
    season_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="CASCADE"),
    )
    title: Mapped[str_256]
    episode_number: Mapped[int]
    duration: Mapped[int | None]
    video_url: Mapped[str | None] = mapped_column(unique=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[created_at]  # Make sure you have added the trigger to the migration.

    # Relationships
    show: Mapped["ShowORM"] = relationship()
    season: Mapped["SeasonORM"] = relationship(back_populates="episodes")
