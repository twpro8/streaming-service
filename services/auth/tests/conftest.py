# ruff: noqa: E402
import json
from unittest.mock import patch

import pytest

from httpx import AsyncClient, ASGITransport

from src.config import settings
from src.managers.db import DBManager
from src.managers.redis import RedisManager
from src.models.base import Base
from src.api.dependencies import get_db, get_redis_manager, get_password_hasher, get_jwt_provider
from src.db import null_pool_engine, null_pool_session_maker
from src.models import *  # noqa
from src.main import app
from src.schemas.users import UserAddDTO
from src.tasks.tasks import send_verification_email


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


class FakeRedis(RedisManager):
    async def connect(self):
        pass

    async def set(self, key, value, expire=None):
        pass

    async def get(self, key):
        return None

    async def getdel(self, key):
        return None

    async def delete(self, key):
        pass

    async def delete_many(self, key):
        pass

    async def close(self):
        pass


async def get_db_null_pool():
    async with DBManager(session_factory=null_pool_session_maker) as db:
        yield db


@pytest.fixture(scope="function")
async def db():
    async for db in get_db_null_pool():
        yield db


# Dependency overrides
app.dependency_overrides[get_db] = get_db_null_pool
app.dependency_overrides[get_redis_manager] = lambda: FakeRedis("uri")


@pytest.fixture(scope="session")
def hasher():
    return get_password_hasher()


@pytest.fixture(scope="session")
def jwt_provider():
    return get_jwt_provider()


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode, hasher):
    async with null_pool_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    users_data = [
        UserAddDTO.model_validate({**u, "password_hash": hasher.hash(u["password"])})
        for u in read_json("users")
    ]

    async with DBManager(session_factory=null_pool_session_maker) as _db:
        await _db.users.add_bulk(users_data)
        await _db.commit()


@pytest.fixture(scope="session")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def captured_verification_email():
    captured = {}

    def mock_send(to_email, code):
        captured["email"] = to_email
        captured["code"] = code
        return {"email": to_email, "code": code}

    with patch.object(send_verification_email, "delay", side_effect=mock_send):
        yield captured


@pytest.fixture(scope="session")
async def get_db_users(ac, setup_database):
    async with DBManager(session_factory=null_pool_session_maker) as _db:
        users = await _db.users.get_filtered()
        return [user.model_dump(mode="json") for user in users]


@pytest.fixture(scope="session")
async def get_active_users(setup_database):
    return [user for user in read_json("users")]


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database, ac):
    res = await ac.post(
        "/v1/auth/signup",
        json={
            "email": "test@gmail.com",
            "password": "some_pass_one_123",
            "first_name": "Test",
            "last_name": "Test",
            "birth_date": "1999-10-22",
            "bio": "What's up? I am a python backend developer. Let's colab!",
        },
    )
    assert res.status_code == 201


@pytest.fixture(scope="session")
async def authed_ac(ac, get_active_users):
    user = get_active_users[0]

    res = await ac.post(
        "/v1/auth/login",
        json={
            "email": user["email"],
            "password": user["password"],
        },
    )
    assert res.status_code == 200
    assert ac.cookies.get("access_token")
    assert ac.cookies.get("refresh_token")
    yield ac


def read_json(file_name: str) -> dict:
    path = f"tests/mock_data/{file_name}.json"
    with open(path, encoding="utf-8") as file_in:
        return json.load(file_in)
