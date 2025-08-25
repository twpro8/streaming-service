from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from src.enums import SortBy, SortOrder
from src.schemas.actors import ShowActorDTO
from src.schemas.genres import ShowGenreDTO
from src.schemas.shows import (
    ShowAddDTO,
    ShowAddRequestDTO,
    ShowPatchRequestDTO,
    ShowPatchDTO,
)
from src.services.base import BaseService
from src.exceptions import (
    ShowNotFoundException,
    UniqueCoverURLException,
    GenreNotFoundException,
    ActorNotFoundException,
)


class ShowService(BaseService):
    async def get_shows(
        self,
        page: int | None,
        per_page: int | None,
        title: str | None,
        description: str | None,
        director: str | None,
        year: int | None,
        year_gt: int | None,
        year_lt: int | None,
        rating: Decimal | None,
        rating_gt: Decimal | None,
        rating_lt: Decimal | None,
        genres_ids: List[int] | None,
        actors_ids: List[UUID] | None,
        sort_by: SortBy | None,
        sort_order: SortOrder | None,
    ):
        shows = await self.db.shows.get_filtered_shows(
            page=page,
            per_page=per_page,
            title=title,
            description=description,
            director=director,
            year=year,
            year_gt=year_gt,
            year_lt=year_lt,
            rating=rating,
            rating_gt=rating_gt,
            rating_lt=rating_lt,
            genres_ids=genres_ids,
            actors_ids=actors_ids,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return shows

    async def get_show(self, show_id: UUID):
        show = await self.db.shows.get_one_or_none_with_rels(id=show_id)
        if show is None:
            raise ShowNotFoundException
        return show

    async def add_show(self, show_data: ShowAddRequestDTO) -> UUID:
        show_id = uuid4()
        _show_data = ShowAddDTO(id=show_id, **show_data.model_dump())
        try:
            await self.db.shows.add_show(_show_data)
        except UniqueCoverURLException:
            raise

        if show_data.genres_ids:
            _show_genres_data = [
                ShowGenreDTO(show_id=show_id, genre_id=genre_id)
                for genre_id in show_data.genres_ids
            ]
            try:
                await self.db.shows_genres.add_show_genres(_show_genres_data)
            except GenreNotFoundException:
                raise
        if show_data.actors_ids:
            _show_actors_data = [
                ShowActorDTO(show_id=show_id, actor_id=actor_id)
                for actor_id in show_data.actors_ids
            ]
            try:
                await self.db.shows_actors.add_show_actors(_show_actors_data)
            except ActorNotFoundException:
                raise

        await self.db.commit()
        return show_id

    async def update_show(self, show_id: UUID, show_data: ShowPatchRequestDTO):
        if not await self.check_show_exists(id=show_id):
            raise ShowNotFoundException

        _show_data = ShowPatchDTO(**show_data.model_dump(exclude_unset=True))

        try:
            await self.db.shows.update_show(
                id=show_id,
                data=_show_data,
                exclude_unset=True,
            )
        except UniqueCoverURLException:
            raise

        if show_data.genres_ids is not None:
            try:
                await self.db.shows_genres.update_show_genres(
                    show_id=show_id,
                    genres_ids=show_data.genres_ids,
                )
            except GenreNotFoundException:
                raise
        if show_data.actors_ids is not None:
            try:
                await self.db.shows_actors.update_show_actors(
                    show_id=show_id,
                    actors_ids=show_data.actors_ids,
                )
            except ActorNotFoundException:
                raise

        await self.db.commit()

    async def delete_show(self, show_id: UUID):
        await self.db.shows.delete(id=show_id)
        await self.db.commit()
