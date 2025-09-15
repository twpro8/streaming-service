from datetime import date
from typing import List

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from src.models.base import Base, uuid_pk, created_at, str_48, str_1024
from src.enums import ZodiacSign


class ActorORM(Base):
    __tablename__ = "actors"
    __table_args__ = (
        UniqueConstraint(
            "first_name",
            "last_name",
            "birth_date",
            name="uq_actor",
        ),
    )

    id: Mapped[uuid_pk]
    first_name: Mapped[str_48]
    last_name: Mapped[str_48]
    birth_date: Mapped[date | None]
    zodiac_sign: Mapped[ZodiacSign | None]
    bio: Mapped[str_1024 | None]
    created_at: Mapped[created_at]
    updated_at: Mapped[created_at]  # Make sure you have added the trigger to the migration.

    # Relationships
    movies: Mapped[List["MovieORM"]] = relationship(
        secondary="movie_actor_associations",
        back_populates="actors",
    )
    shows: Mapped[List["ShowORM"]] = relationship(
        secondary="show_actor_associations",
        back_populates="actors",
    )

    def __repr__(self):
        return (
            f"<ActorORM("
            f"id={self.id!r}, "
            f"first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"birth_date={self.birth_date!r}, "
            f"zodiac_sign={self.zodiac_sign!r}, "
            f"bio={self.bio!r}, "
            f"created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r})>"
        )
