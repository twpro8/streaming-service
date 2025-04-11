# ruff: noqa

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class CommentORM(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    film_id: Mapped[int] = mapped_column(ForeignKey("films.id", ondelete="CASCADE"), nullable=True)
    series_id: Mapped[int] = mapped_column(
        ForeignKey("series.id", ondelete="CASCADE"), nullable=True
    )
    text: Mapped[str]

    # Relationships
    film: Mapped["FilmORM"] = relationship(back_populates="comments")
    series: Mapped["SeriesORM"] = relationship(back_populates="comments")
