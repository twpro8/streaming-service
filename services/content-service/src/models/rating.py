from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy import UniqueConstraint, DECIMAL, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base


class RatingORM(Base):
    __tablename__ = "ratings"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[int]
    content_id: Mapped[UUID]
    value: Mapped[Decimal] = mapped_column(DECIMAL(3, 1))

    __table_args__ = (
        UniqueConstraint("user_id", "content_id"),
        CheckConstraint("value >= 0 AND value <= 10"),
    )


class RatingAggregateORM(Base):
    __tablename__ = "rating_aggregates"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    content_id: Mapped[UUID]
    rating_sum: Mapped[Decimal] = mapped_column(DECIMAL(10, 1), default=Decimal("0.0"))
    rating_count: Mapped[int] = mapped_column(default=0)
    rating_avg: Mapped[Decimal] = mapped_column(DECIMAL(3, 1), default=Decimal("0.0"))
