from typing import Any, AsyncGenerator
from uuid import uuid4, UUID

import pytest

from httpx import AsyncClient, ASGITransport

from src.config import settings
from src.api.dependencies import get_db, get_admin, get_current_user_id
from src.db import null_pool_engine, null_pool_session_maker
from src.managers.db import DBManager
from src.models.base import Base
from src.models import *  # noqa
from src.main import app
from src.schemas.actors import ActorAddDTO, MovieActorDTO, ShowActorDTO
from src.schemas.comments import CommentAddDTO
from src.schemas.countries import CountryAddDTO
from src.schemas.directors import DirectorAddDTO
from src.schemas.episodes import EpisodeAddDTO
from src.schemas.languages import LanguageAddDTO
from src.schemas.movies import MovieAddDTO
from src.schemas.genres import GenreAddDTO, MovieGenreDTO, ShowGenreDTO
from src.schemas.seasons import SeasonAddDTO
from src.schemas.shows import ShowAddDTO
from tests.utils import read_json


user_id = uuid4()


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool() -> AsyncGenerator[Any, Any]:
    async with DBManager(session_factory=null_pool_session_maker) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[Any, Any]:
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool  # noqa
app.dependency_overrides[get_admin] = lambda: None  # noqa
app.dependency_overrides[get_current_user_id] = lambda: user_id  # The number is a user_id | # noqa


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with null_pool_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    movies_data = [MovieAddDTO.model_validate(obj) for obj in read_json("movies")]
    shows_data = [ShowAddDTO.model_validate(obj) for obj in read_json("shows")]
    seasons_data = [SeasonAddDTO.model_validate(obj) for obj in read_json("seasons")]
    episodes_data = [EpisodeAddDTO.model_validate(obj) for obj in read_json("episodes")]
    directors_data = [DirectorAddDTO.model_validate(obj) for obj in read_json("actors")]
    actors_data = [ActorAddDTO.model_validate(obj) for obj in read_json("actors")]
    genres_data = [GenreAddDTO.model_validate(obj) for obj in read_json("genres")]
    movies_genres_data = [MovieGenreDTO.model_validate(obj) for obj in read_json("movies_genres")]
    shows_genres_data = [ShowGenreDTO.model_validate(obj) for obj in read_json("shows_genres")]
    movies_actors_data = [MovieActorDTO.model_validate(obj) for obj in read_json("movies_actors")]
    shows_actors_data = [ShowActorDTO.model_validate(obj) for obj in read_json("shows_actors")]
    comments_data = [
        CommentAddDTO.model_validate({**obj, "user_id": user_id}) for obj in read_json("comments")
    ]
    languages = [LanguageAddDTO.model_validate(obj) for obj in read_json("languages")]
    countries = [CountryAddDTO.model_validate(obj) for obj in read_json("countries")]

    async with DBManager(session_factory=null_pool_session_maker) as db_:
        await db_.movies.add_bulk(movies_data)
        await db_.shows.add_bulk(shows_data)
        await db_.seasons.add_bulk(seasons_data)
        await db_.episodes.add_bulk(episodes_data)
        await db_.genres.add_bulk(genres_data)
        await db_.movies_genres.add_bulk(movies_genres_data)
        await db_.shows_genres.add_bulk(shows_genres_data)
        await db_.directors.add_bulk(directors_data)
        await db_.actors.add_bulk(actors_data)
        await db_.movies_actors.add_bulk(movies_actors_data)
        await db_.shows_actors.add_bulk(shows_actors_data)
        await db_.comments.add_bulk(comments_data)
        await db_.languages.add_bulk(languages)
        await db_.countries.add_bulk(countries)
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def get_shows_ids():
    data = read_json("shows")
    return [show_id["id"] for show_id in data]


@pytest.fixture
async def created_genres(ac):
    ids = []
    for name in ["TestGenre1", "TestGenre2", "TestGenre3"]:
        res = await ac.post("/v1/genres", json={"name": name})
        assert res.status_code == 201
        ids.append(res.json()["data"]["id"])
    yield ids
    for genre_id in ids:
        await ac.delete(f"/v1/genres/{genre_id}")


@pytest.fixture(scope="session")
async def max_pagination():
    return {"page": 1, "per_page": 30}


@pytest.fixture
async def get_all_movies_with_rels(ac):
    movies = []
    for movie in read_json("movies"):
        res = await ac.get(f"/v1/movies/{movie['id']}")
        assert res.status_code == 200
        data = res.json()["data"]
        movies.append(data)
    return movies


@pytest.fixture
async def created_movies(ac):
    movies = []
    try:
        for i in range(700, 703):
            res = await ac.post(
                "/v1/movies",
                json={
                    "title": f"Python Movie{i}",
                    "description": f"Hola Amigo{i}",
                    "release_date": "1777-01-01",
                    "duration": 135,
                },
            )
            assert res.status_code == 201
            movie = res.json()["data"]
            movies.append(movie)
        yield movies
    finally:
        for movie in movies:
            await ac.delete(f"/v1/movies/{movie['id']}")


@pytest.fixture
async def created_shows(ac):
    shows = []
    try:
        for i in range(704, 707):
            res = await ac.post(
                "/v1/shows",
                json={
                    "title": f"Python Movie{i}",
                    "description": f"Hola Amigo{i}",
                    "release_date": "1777-01-01",
                },
            )
            assert res.status_code == 201
            show = res.json()["data"]
            shows.append(show)
        yield shows
    finally:
        for s in shows:
            await ac.delete(f"/v1/shows/{s['id']}")


@pytest.fixture
async def created_languages(ac):
    langs = []
    mock_data = ["he", "vi", "th", "id", "no"]
    try:
        for code in mock_data:
            res = await ac.post("/v1/languages", json={"code": code})
            assert res.status_code == 201
            lang = res.json()["data"]
            langs.append(lang)
        yield langs
    finally:
        for s in langs:
            await ac.delete(f"/v1/shows/{s['id']}")


@pytest.fixture
async def created_countries(ac):
    countries = []
    mock_data = ["EG", "NG", "SE", "FI", "NZ"]
    try:
        for code in mock_data:
            res = await ac.post("/v1/countries", json={"code": code})
            assert res.status_code == 201
            country = res.json()["data"]
            countries.append(country)
        yield countries
    finally:
        for s in countries:
            await ac.delete(f"/v1/shows/{s['id']}")


@pytest.fixture(scope="function")
async def get_all_comments():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        comments = await db_.comments.get_filtered()
        return [comment.model_dump() for comment in comments]


@pytest.fixture(scope="session")
async def get_all_movies():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        movies = await db_.movies.get_filtered()
        return [movie.model_dump() for movie in movies]


@pytest.fixture(scope="session")
async def get_all_shows():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        shows = await db_.shows.get_filtered()
        return [show.model_dump() for show in shows]


@pytest.fixture(scope="session")
async def get_all_genres():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        genres = await db_.genres.get_filtered()
        return [genre.model_dump() for genre in genres]


@pytest.fixture(scope="session")
async def get_all_actors():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        actors = await db_.actors.get_filtered()
        return [actor.model_dump() for actor in actors]


@pytest.fixture(scope="session")
async def get_all_directors():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        directors = await db_.directors.get_filtered()
        return [director.model_dump() for director in directors]


@pytest.fixture(scope="session")
async def get_all_shows_with_rels(ac):
    shows = []
    for s in read_json("shows"):
        res = await ac.get(f"/v1/shows/{s['id']}")
        assert res.status_code == 200
        data = res.json()["data"]
        shows.append(data)
    return shows


@pytest.fixture(scope="session")
async def get_all_seasons():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        seasons = await db_.seasons.get_filtered()
        return [season.model_dump() for season in seasons]


@pytest.fixture(scope="session")
async def get_all_episodes():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        episodes = await db_.episodes.get_filtered()
        return [episode.model_dump() for episode in episodes]


@pytest.fixture(scope="session")
async def get_all_languages():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        languages = await db_.languages.get_filtered()
        return [lang.model_dump() for lang in languages]


@pytest.fixture(scope="session")
async def get_all_countries():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        countries = await db_.countries.get_filtered()
        return [country.model_dump() for country in countries]


@pytest.fixture(scope="session")
async def current_user_id() -> UUID:
    return user_id
