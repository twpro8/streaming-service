import logging
from typing import Type

from pydantic import BaseModel
from sqlalchemy import select, insert, delete, update
from sqlalchemy.exc import NoResultFound

from src.enums import SortOrder
from src.exceptions import ObjectNotFoundException
from src.repositories.mappers.base import DataMapper


log = logging.getLogger(__name__)


class BaseRepository:
    model = None
    mapper: Type[DataMapper] = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(
        self,
        page: int = None,
        per_page: int = None,
        *filter,
        **filter_by,
    ) -> list[BaseModel]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        query = self._paginate(query, page, per_page)
        return await self._execute_and_map_all(query)

    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        return await self._execute_and_map_one(query)

    async def get_one_or_none(self, **filter_by) -> BaseModel | None:
        query = select(self.model).filter_by(**filter_by)
        return await self._execute_and_map_one_or_none(query)

    async def add(self, data: BaseModel) -> None:
        stmt = insert(self.model).values(**data.model_dump())
        await self.session.execute(stmt)

    async def add_bulk(self, data: list[BaseModel]) -> None:
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

    async def _execute_and_map_one(self, query) -> BaseModel:
        res = await self.session.execute(query)
        try:
            model = res.scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def _execute_and_map_one_or_none(self, query) -> BaseModel | None:
        res = await self.session.execute(query)
        model = res.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def _execute_and_map_all(self, query) -> list[BaseModel]:
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(m) for m in res.scalars().all()]

    @staticmethod
    def _paginate(query, page: int, per_page: int):
        """Applies limit and offset to query."""
        if page is not None and per_page is not None:
            return query.limit(per_page).offset((page - 1) * per_page)
        return query

    @staticmethod
    def _apply_sorting(
        query,
        model,
        sort_by: str = "id",
        sort_order: str = "desc",
    ):
        """Applies sorting to query."""
        if sort_by:
            column = getattr(model, sort_by, None)
            if column is not None:
                if sort_order == SortOrder.desc:
                    return query.order_by(column.desc())
                return query.order_by(column.asc())
        return query

    def _apply_sorting_and_pagination(
        self,
        query,
        model,
        sort_by: str,
        sort_order: str,
        page: int = None,
        per_page: int = None,
    ):
        query = self._apply_sorting(query, model, sort_by, sort_order)
        query = self._paginate(query, page, per_page)
        return query
