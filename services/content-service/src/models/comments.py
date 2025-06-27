# ruff: noqa

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
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
    film_id: Mapped[UUID] = mapped_column(ForeignKey("films.id", ondelete="CASCADE"), nullable=True)
    series_id: Mapped[UUID] = mapped_column(
        ForeignKey("series.id", ondelete="CASCADE"), nullable=True
    )
    text: Mapped[str] = mapped_column(String(255))

    # Relationships
    film: Mapped["FilmORM"] = relationship(back_populates="comments")
    series: Mapped["SeriesORM"] = relationship(back_populates="comments")
