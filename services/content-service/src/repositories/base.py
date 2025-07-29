import logging
from datetime import date
from decimal import Decimal
from typing import Type, List

from asyncpg import UniqueViolationError, ForeignKeyViolationError
from pydantic import BaseModel
from sqlalchemy import select, insert, delete, update, func
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.exceptions import (
    ObjectNotFoundException,
    ObjectAlreadyExistsException,
    ForeignKeyViolationException,
)
from src.repositories.mappers.base import DataMapper
from src.repositories.utils import normalize_for_insert


log = logging.getLogger(__name__)


class BaseRepository:
    model = None
    schema: Type[BaseModel] = None
    mapper: Type[DataMapper] = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, page: int = None, per_page: int = None, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        if page is not None and per_page is not None:
            query = query.limit(per_page).offset((page - 1) * per_page)
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in res.scalars().all()]

    async def get_filtered_films_or_series(
        self,
        page,
        per_page,
        title: str | None,
        description: str | None,
        director: str | None,
        release_year: date | None,
        release_year_ge: date | None,
        release_year_le: date | None,
        rating: Decimal | None,
        rating_ge: Decimal | None,
        rating_le: Decimal | None,
    ):
        query = select(self.model)
        if title is not None:
            query = query.filter(func.lower(self.model.title).contains(title.strip().lower()))
        if description is not None:
            query = query.filter(
                func.lower(self.model.description).contains(description.strip().lower())
            )
        if director is not None:
            query = query.filter(func.lower(self.model.director).contains(director.strip().lower()))
        if release_year is not None:
            query = query.filter(self.model.release_year == release_year)
        if release_year_ge is not None:
            query = query.filter(self.model.release_year >= release_year_ge)
        if release_year_le is not None:
            query = query.filter(self.model.release_year <= release_year_le)
        if rating is not None:
            query = query.filter(self.model.rating == rating)
        if rating_ge is not None:
            query = query.filter(self.model.rating >= rating_ge)
        if rating_le is not None:
            query = query.filter(self.model.rating <= rating_le)

        query = query.order_by(self.model.id).limit(per_page).offset((page - 1) * per_page)
        res = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(model) for model in res.scalars().all()]

    async def get_objects_by_ids(self, ids: List[int]):
        query = select(self.model).filter(self.model.id.in_(ids))
        res = await self.session.execute(query)
        objects = res.scalars().all()
        return [self.mapper.map_to_domain_entity(obj) for obj in objects]

    async def get_one(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(query)
        try:
            model = res.scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(query)
        model = res.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        data = normalize_for_insert(data.model_dump())
        stmt = insert(self.model).values(**data).returning(self.model)
        try:
            res = await self.session.execute(stmt)
        except IntegrityError as exc:
            if isinstance(exc.orig.__cause__, UniqueViolationError):
                raise ObjectAlreadyExistsException from exc
            elif isinstance(exc.orig.__cause__, ForeignKeyViolationError):
                raise ForeignKeyViolationException from exc
            else:
                log.exception(f"Unknown error: failed to add data to database, input data: {data}")
                raise exc
        model = res.scalars().one()
        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: list[BaseModel]):
        stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(stmt)

    async def update(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        data = normalize_for_insert(data.model_dump(exclude_unset=exclude_unset))
        stmt = update(self.model).values(**data).filter_by(**filter_by)
        try:
            await self.session.execute(stmt)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            if isinstance(cause, UniqueViolationError):
                raise ObjectAlreadyExistsException from exc
            else:
                log.exception(
                    f"Unknown error: failed to update data in database, input data: {data}"
                )
                raise exc

    async def delete(self, **filter_by) -> None:
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)
