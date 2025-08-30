from typing import List
from uuid import UUID

from sqlalchemy import UUID as PG_UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, uuid_pk, created_at, str_256


class SeasonORM(Base):
    __tablename__ = "seasons"
    __table_args__ = (
        UniqueConstraint(
            "show_id",
            "season_number",
            name="uq_season",
        ),
    )

    id: Mapped[uuid_pk]
    show_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("shows.id", ondelete="CASCADE"),
    )
    title: Mapped[str_256]
    season_number: Mapped[int]
    created_at: Mapped[created_at]
    updated_at: Mapped[created_at]  # Make sure you have added the trigger to the migration.

    # Relationships
    show: Mapped["ShowORM"] = relationship(back_populates="seasons")
    episodes: Mapped[List["EpisodeORM"]] = relationship(back_populates="season")
