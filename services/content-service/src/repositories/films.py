import logging
from datetime import date
from typing import List
from uuid import UUID

from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import select, func, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.exceptions import UniqueCoverURLException, UniqueVideoURLException
from src.models import FilmORM, FilmGenreORM
from src.models.actors import FilmActorORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FilmDataMapper, FilmWithRelsDataMapper
from src.schemas.films import FilmDTO


log = logging.getLogger(__name__)


class FilmRepository(BaseRepository):
    model = FilmORM
    schema = FilmDTO
    mapper = FilmDataMapper

    async def get_filtered_films(
        self,
        page: int | None,
        per_page: int | None,
        genres_ids: List[int] | None,
        actors_ids: List[UUID] | None,
        sort_by: str | None,
        sort_order: str | None,
        **kwargs,
    ):
        filters = {
            "title": lambda v: func.lower(self.model.title).contains(v.strip().lower()),
            "description": lambda v: func.lower(self.model.description).contains(v.strip().lower()),
            "director": lambda v: func.lower(self.model.director).contains(v.strip().lower()),
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
                FilmGenreORM.film_id == self.model.id, FilmGenreORM.genre_id.in_(genres_ids)
            )
            query = query.filter(genre_filter)
        if actors_ids:
            actor_filter = exists().where(
                FilmActorORM.film_id == self.model.id, FilmActorORM.actor_id.in_(actors_ids)
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
        return FilmWithRelsDataMapper.map_to_domain_entity(model)

    async def add_film(self, data: BaseModel) -> None:
        try:
            await self.add(data)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "films_cover_url_key":
                        raise UniqueCoverURLException from exc
            log.exception("Unknown error: failed to add data to database, input data: %s", data)
            raise

    async def update_film(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        try:
            await self.update(data, exclude_unset=exclude_unset, **filter_by)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "films_cover_url_key":
                        raise UniqueCoverURLException from exc
                    case "films_video_url_key":
                        raise UniqueVideoURLException from exc
            log.exception("Unknown error: failed to update data in database, input data: %s", data)
            raise
