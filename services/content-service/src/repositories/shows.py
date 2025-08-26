import logging
from datetime import date
from typing import List
from uuid import UUID

from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import select, func, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.enums import SortBy, SortOrder
from src.exceptions import UniqueCoverURLException
from src.models import ShowORM, ShowGenreORM
from src.models.associations import ShowActorORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import ShowDataMapper, ShowWithRelsDataMapper
from src.schemas.shows import ShowDTO


log = logging.getLogger(__name__)


class ShowRepository(BaseRepository):
    model = ShowORM
    schema = ShowDTO
    mapper = ShowDataMapper

    async def get_filtered_shows(
        self,
        page: int | None,
        per_page: int | None,
        genres_ids: List[int] | None,
        actors_ids: List[UUID] | None,
        sort_by: SortBy | None,
        sort_order: SortOrder | None,
        **kwargs,
    ):
        filters = {
            "title": lambda v: func.lower(self.model.title).contains(v.strip().lower()),
            "description": lambda v: func.lower(self.model.description).contains(v.strip().lower()),
            "year": lambda v: (self.model.release_year >= date(v, 1, 1))
            & (self.model.release_year <= date(v, 12, 31)),
            "year_gt": lambda v: self.model.release_year > date(v, 1, 1),
            "year_lt": lambda v: self.model.release_year < date(v, 1, 1),
            "rating": lambda v: self.model.rating == v,
            "rating_gt": lambda v: self.model.rating > v,
            "rating_lt": lambda v: self.model.rating < v,
        }

        query = select(self.model)
        if genres_ids:
            genre_filter = exists().where(
                ShowGenreORM.show_id == self.model.id,
                ShowGenreORM.genre_id.in_(genres_ids),
            )
            query = query.filter(genre_filter)
        if actors_ids:
            actor_filter = exists().where(
                ShowActorORM.show_id == self.model.id,
                ShowActorORM.actor_id.in_(actors_ids),
            )
            query = query.filter(actor_filter)

        for key, value in kwargs.items():
            if key in filters and value is not None:
                query = query.filter(filters[key](value))

        sort_by = "release_year" if sort_by == "year" else sort_by

        # apply sorting and pagination
        query = self._apply_sorting_and_pagination(
            query=query,
            model=self.model,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page,
        )

        return await self._execute_and_map_all(query)

    async def get_one_or_none_with_rels(self, **filter_by):
        query = (
            select(self.model)
            .options(selectinload(self.model.genres), selectinload(self.model.actors))
            .filter_by(**filter_by)
        )
        res = await self.session.execute(query)
        model = res.scalars().one_or_none()
        if model is None:
            return None
        return ShowWithRelsDataMapper.map_to_domain_entity(model)

    async def add_show(self, data: BaseModel) -> None:
        try:
            await self.add(data)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "shows_cover_url_key":
                        raise UniqueCoverURLException from exc
            log.exception("Unknown error: failed to add data to database, input data: %s", data)
            raise

    async def update_show(
        self,
        data: BaseModel,
        exclude_unset: bool = False,
        **filter_by,
    ) -> None:
        try:
            await self.update(data, exclude_unset=exclude_unset, **filter_by)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "shows_cover_url_key":
                        raise UniqueCoverURLException from exc
            log.exception("Unknown error: failed to update data in database, input data: %s", data)
            raise
