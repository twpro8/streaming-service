from uuid import UUID

from sqlalchemy.orm import Mapped

from src.models.base import Base, uuid_pk, created_at, str_32, str_512


class CommentORM(Base):
    __tablename__ = "comments"

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID]
    content_id: Mapped[UUID]
    content_type: Mapped[str_32]
    comment: Mapped[str_512]
    created_at: Mapped[created_at]
    updated_at: Mapped[created_at]  # Make sure you have added the trigger to the migration.
