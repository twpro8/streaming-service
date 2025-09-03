from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from src.enums import SortBy, SortOrder
from src.schemas.actors import MovieActorDTO
from src.schemas.countries import MovieCountryDTO
from src.schemas.directors import MovieDirectorDTO
from src.schemas.movies import (
    MovieAddRequestDTO,
    MovieAddDTO,
    MoviePatchRequestDTO,
    MoviePatchDTO,
)
from src.schemas.genres import MovieGenreDTO
from src.services.base import BaseService
from src.exceptions import (
    MovieNotFoundException,
    CoverUrlAlreadyExistsException,
    VideoUrlAlreadyExistsException,
    GenreNotFoundException,
    ActorNotFoundException,
    DirectorNotFoundException,
    CountryNotFoundException,
    MovieAlreadyExistsException,
)


class MovieService(BaseService):
    async def get_movies(
        self,
        page: int | None,
        per_page: int | None,
        title: str | None,
        description: str | None,
        year: int | None,
        year_gt: int | None,
        year_lt: int | None,
        rating: Decimal | None,
        rating_gt: Decimal | None,
        rating_lt: Decimal | None,
        directors_ids: List[UUID] | None,
        actors_ids: List[UUID] | None,
        genres_ids: List[int] | None,
        countries_ids: List[int] | None,
        sort_by: SortBy | None,
        sort_order: SortOrder | None,
    ):
        movies = await self.db.movies.get_filtered_movies(
            page=page,
            per_page=per_page,
            title=title,
            description=description,
            year=year,
            year_gt=year_gt,
            year_lt=year_lt,
            rating=rating,
            rating_gt=rating_gt,
            rating_lt=rating_lt,
            directors_ids=directors_ids,
            actors_ids=actors_ids,
            genres_ids=genres_ids,
            countries_ids=countries_ids,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return movies

    async def get_movie(self, movie_id: UUID):
        movie = await self.db.movies.get_one_or_none_with_rels(id=movie_id)
        if movie is None:
            raise MovieNotFoundException
        return movie

    async def add_movie(self, movie_data: MovieAddRequestDTO) -> UUID:
        movie_id = uuid4()
        _movie_data = MovieAddDTO(id=movie_id, **movie_data.model_dump())
        try:
            await self.db.movies.add_movie(_movie_data)
        except (MovieAlreadyExistsException, CoverUrlAlreadyExistsException):
            raise

        if movie_data.genres_ids:
            _movie_genres_data = [
                MovieGenreDTO(movie_id=movie_id, genre_id=genre_id)
                for genre_id in movie_data.genres_ids
            ]
            try:
                await self.db.movies_genres.add_movie_genres(_movie_genres_data)
            except GenreNotFoundException:
                raise
        if movie_data.actors_ids:
            _movie_actors_data = [
                MovieActorDTO(movie_id=movie_id, actor_id=actor_id)
                for actor_id in movie_data.actors_ids
            ]
            try:
                await self.db.movies_actors.add_movie_actors(_movie_actors_data)
            except ActorNotFoundException:
                raise
        if movie_data.directors_ids:
            _movie_directors_data = [
                MovieDirectorDTO(movie_id=movie_id, director_id=director_id)
                for director_id in movie_data.directors_ids
            ]
            try:
                await self.db.movies_directors.add_movie_directors(_movie_directors_data)
            except DirectorNotFoundException:
                raise
        if movie_data.countries_ids:
            _movie_countries_data = [
                MovieCountryDTO(movie_id=movie_id, country_id=country_id)
                for country_id in movie_data.countries_ids
            ]
            try:
                await self.db.movies_countries.add_movie_countries(_movie_countries_data)
            except CountryNotFoundException:
                raise

        await self.db.commit()
        return movie_id

    async def update_movie(self, movie_id: UUID, movie_data: MoviePatchRequestDTO):
        _movie_data = MoviePatchDTO(**movie_data.model_dump(exclude_unset=True))

        try:
            await self.db.movies.update_movie(id=movie_id, data=_movie_data, exclude_unset=True)
        except (
            MovieNotFoundException,
            MovieAlreadyExistsException,
            CoverUrlAlreadyExistsException,
            VideoUrlAlreadyExistsException,
        ):
            raise

        if movie_data.genres_ids is not None:
            try:
                await self.db.movies_genres.update_movie_genres(
                    movie_id=movie_id,
                    genres_ids=movie_data.genres_ids,
                )
            except GenreNotFoundException:
                raise
        if movie_data.actors_ids is not None:
            try:
                await self.db.movies_actors.update_movie_actors(
                    movie_id=movie_id,
                    actors_ids=movie_data.actors_ids,
                )
            except ActorNotFoundException:
                raise
        if movie_data.directors_ids is not None:
            try:
                await self.db.movies_directors.update_movie_directors(
                    movie_id=movie_id,
                    directors_ids=movie_data.directors_ids,
                )
            except DirectorNotFoundException:
                raise
        if movie_data.countries_ids is not None:
            try:
                await self.db.movies_countries.update_movie_countries(
                    movie_id=movie_id,
                    countries_ids=movie_data.countries_ids,
                )
            except CountryNotFoundException:
                raise

        await self.db.commit()

    async def delete_movie(self, movie_id: UUID):
        await self.db.movies.delete(id=movie_id)
        await self.db.commit()
