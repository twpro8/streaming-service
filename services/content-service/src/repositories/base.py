from typing import List

from pydantic import BaseModel
from sqlalchemy import select, insert
from sqlalchemy.exc import NoResultFound

from src.exceptions import ObjectNotFoundException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    schema: BaseModel = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
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

    async def add_one(self, data: BaseModel):
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        res = await self.session.execute(stmt)
        model = res.scalars().one()
        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: list[BaseModel]):
        stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(stmt)
