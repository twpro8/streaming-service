from pydantic import BaseModel
from sqlalchemy import insert, select, delete, update
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    schema: BaseModel = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, limit: int = None, offset: int = None, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        if limit is not None and offset is not None:
            query = query.limit(limit).offset(offset)
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

    async def add_one(self, data: BaseModel):
        try:
            stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
            res = await self.session.execute(stmt)
            model = res.scalars().one()
        except IntegrityError:
            raise ObjectAlreadyExistsException
        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: list[BaseModel]):
        stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(stmt)

    async def update(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        _model_dump = data.model_dump(exclude_unset=exclude_unset)
        if not _model_dump:
            return
        stmt = update(self.model).values(**_model_dump).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        if res.rowcount == 0:
            raise ObjectNotFoundException

    async def delete(self, **filter_by) -> None:
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)
