from typing import Type

from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException
from src.repositories.mappers.base import DataMapper


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
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            res = await self.session.execute(stmt)
        except IntegrityError as exc:
            raise ObjectAlreadyExistsException from exc
        model = res.scalars().one()
        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: list[BaseModel]):
        stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(stmt)

    async def update(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        stmt = (
            update(self.model)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .filter_by(**filter_by)
        )
        await self.session.execute(stmt)

    async def delete(self, **filter_by) -> None:
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)
