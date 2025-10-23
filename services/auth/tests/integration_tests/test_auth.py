import asyncio
from datetime import datetime, timezone, timedelta
from itertools import islice

import pytest

from src.config import settings
from src.api.dependencies import get_jwt_provider


jwt_provider = get_jwt_provider()


@pytest.mark.parametrize(
    "email, password, first_name",
    (
        ("valid_email@gmail.com", "valid_password", "valid"),
        ("valid_email_1@gmail.com", "valid_password_1", "valid_1"),
    ),
)
async def test_signup_valid(ac, email, password, first_name):
    res = await ac.post(
        "/v1/auth/signup",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
        },
    )
    assert res.status_code == 201


@pytest.mark.parametrize(
    "email, password, first_name, last_name, birth_date, bio",
    (
        (
            "valid_email_2@gmail.com",
            "valid_password_2",
            "valid_2",
            "valid_2",
            "1999-01-01",
            "valid_bio_2",
        ),
        (
            "valid_email_3@gmail.com",
            "valid_password_3",
            "valid_3",
            "valid_3",
            "1999-01-01",
            "valid_bio_3",
        ),
    ),
)
async def test_signup_valid_with_optional(
    ac, email, password, first_name, last_name, birth_date, bio
):
    res = await ac.post(
        "/v1/auth/signup",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "bio": bio,
        },
    )
    assert res.status_code == 201


async def test_signup_on_conflict(ac, get_users):
    for user in islice(get_users, 2):
        res = await ac.post("/v1/auth/signup", json=user)
        assert res.status_code == 409, f"Expected 409 for duplicate signup, got {res.status_code}"
        assert "detail" in res.json()


@pytest.mark.parametrize(
    "field, value",
    (
        ("email", "invalid_email"),
        ("password", "p" * 5),
        ("password", "p" * 129),
        ("first_name", "f"),
        ("first_name", "f" * 49),
        ("last_name", "l"),
        ("last_name", "l" * 49),
        ("birth_date", "invalid_date_type"),
        ("birth_date", "1899-01-01"),
        ("birth_date", "2300-01-01"),
        ("bio", "b"),
        ("bio", "b" * 1025),
        ("extra", "unknown"),
    ),
)
async def test_signup_invalid(ac, field, value):
    body = {
        "email": "valid_test@gmail.com",
        "password": "valid_password123",
        "first_name": "John",
        "last_name": "Davis",
        "birth_date": "1999-01-01",
        "bio": "I have a valid bio!",
        field: value,
    }
    res = await ac.post("/v1/auth/signup", json=body)
    assert res.status_code == 422
    assert "detail" in res.json()
    assert res.json()["detail"][0]["loc"][1] == field
    assert res.json()["detail"][0]["input"] == value


async def test_login(ac, get_users):
    for user in islice(get_users, 2):
        ac.cookies.delete("access_token")
        ac.cookies.delete("refresh_token")

        res = await ac.post(
            "/v1/auth/login",
            json={
                "email": user["email"],
                "password": user["password"],
            },
        )
        assert res.status_code == 200

        access = ac.cookies.get("access_token")
        refresh = ac.cookies.get("refresh_token")

        assert access is not None
        assert refresh is not None

        access_payload = jwt_provider.decode_token(access)
        refresh_payload = jwt_provider.decode_token(refresh)

        assert access_payload.get("id")
        assert access_payload.get("name")
        assert access_payload.get("first_name")

        assert access_payload["email"] == user["email"]
        assert access_payload.get("exp")
        assert refresh_payload["sub"] == access_payload["id"]
        assert refresh_payload.get("exp")

        now = datetime.now(timezone.utc)
        access_exp = datetime.fromtimestamp(access_payload["exp"], tz=timezone.utc)
        refresh_exp = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)

        assert (
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES - 1)
            <= (access_exp - now)
            <= timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)
        )
        assert (
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS - 1)
            <= (refresh_exp - now)
            <= timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS + 1)
        )


@pytest.mark.parametrize(
    "field, value",
    (
        ("email", "invalid_email"),
        ("password", "123"),
        ("extra", "unknown"),
    ),
)
async def test_login_invalid(ac, get_users, field, value):
    user = get_users[0]
    body = {
        "email": user["email"],
        "password": user["password"],
        field: value,
    }

    ac.cookies.delete("access_token")
    ac.cookies.delete("refresh_token")

    res = await ac.post("/v1/auth/login", json=body)
    assert res.status_code == 422
    assert "detail" in res.json()
    assert res.json()["detail"][0]["loc"][1] == field
    assert res.json()["detail"][0]["input"] == value


async def test_login_with_wrong_password(ac, get_users):
    ac.cookies.delete("access_token")
    ac.cookies.delete("refresh_token")

    for user in islice(get_users, 2):
        res = await ac.post(
            "/v1/auth/login",
            json={
                "email": user["email"],
                "password": "wrong_password123",
            },
        )
        assert res.status_code == 401
        assert "detail" in res.json()


async def test_login_user_not_found(ac, get_users):
    res = await ac.post(
        "/v1/auth/login",
        json={
            "email": "no_such_user@gmail.com",
            "password": "some_password123",
        },
    )
    assert res.status_code == 404
    assert "detail" in res.json()


async def test_refresh_tokens(authed_ac):
    old_access = authed_ac.cookies.get("access_token")
    old_refresh = authed_ac.cookies.get("refresh_token")
    assert old_access and old_refresh

    await asyncio.sleep(1)  # wait one sec so that exp changed

    res = await authed_ac.post("/v1/auth/refresh")
    assert res.status_code == 200

    new_access = authed_ac.cookies.get("access_token")
    new_refresh = authed_ac.cookies.get("refresh_token")
    assert new_access and new_refresh

    assert old_access != new_access
    assert old_refresh != new_refresh

    access_payload = jwt_provider.decode_token(new_access)
    refresh_payload = jwt_provider.decode_token(new_refresh)

    assert access_payload.get("id")
    assert access_payload.get("email")
    assert access_payload.get("exp")
    assert refresh_payload.get("sub") == access_payload["id"]
    assert refresh_payload.get("exp")

    now = datetime.now(timezone.utc)
    access_exp = datetime.fromtimestamp(access_payload["exp"], tz=timezone.utc)
    refresh_exp = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)

    assert (
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES - 1)
        <= (access_exp - now)
        <= timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)
    )

    assert (
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS - 1)
        <= (refresh_exp - now)
        <= timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS + 1)
    )


async def test_logout(authed_ac):
    res = await authed_ac.post("/v1/auth/logout")
    assert res.status_code == 200

    access = authed_ac.cookies.get("access_token")
    refresh = authed_ac.cookies.get("refresh_token")

    assert access is None, "Access token should be cleared after logout"
    assert refresh is None, "Refresh token should be cleared after logout"
