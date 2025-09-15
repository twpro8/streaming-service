from uuid import UUID
from decimal import Decimal

from sqlalchemy import UniqueConstraint, CheckConstraint, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, uuid_pk


class RatingORM(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("user_id", "content_id", name="uq_rating"),
        CheckConstraint("value >= 0 AND value <= 10"),
    )

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID]
    content_id: Mapped[UUID]
    value: Mapped[Decimal] = mapped_column(DECIMAL(3, 1))


class RatingAggregateORM(Base):
    __tablename__ = "rating_aggregates"

    content_id: Mapped[uuid_pk]
    rating_sum: Mapped[Decimal] = mapped_column(DECIMAL(10, 1), default=Decimal("0.0"))
    rating_count: Mapped[int] = mapped_column(default=0)
    rating_avg: Mapped[Decimal] = mapped_column(DECIMAL(3, 1), default=Decimal("0.0"))
