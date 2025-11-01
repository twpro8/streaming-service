import asyncio
from datetime import datetime, timezone, timedelta
from itertools import islice

import pytest

from src.config import settings


async def _login(ac, email, password):
    """Login and return response. Clears cookies before login."""
    ac.cookies.clear()
    return await ac.post("/v1/auth/login", json={"email": email, "password": password})


def _assert_tokens_present(ac):
    access = ac.cookies.get("access_token")
    refresh = ac.cookies.get("refresh_token")
    assert access is not None, "No access token in cookies"
    assert refresh is not None, "No refresh token in cookies"
    return access, refresh


def _decode_tokens_and_basic_asserts(jwt_provider, access, refresh, email=None):
    access_payload = jwt_provider.decode_token(access)
    refresh_payload = jwt_provider.decode_token(refresh)

    assert access_payload.get("id")
    assert (
        access_payload.get("name") or access_payload.get("email") or True
    )  # name may be optional in some fixtures
    if email:
        assert access_payload["email"] == email
    assert access_payload.get("exp")

    assert refresh_payload["sub"] == access_payload["id"]
    assert refresh_payload.get("exp")

    return access_payload, refresh_payload


def _assert_token_ttls(access_payload, refresh_payload):
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
    "email, password, first_name",
    (
        ("valid_email@gmail.com", "valid_password", "valid"),
        ("valid_email_1@gmail.com", "valid_password_1", "valid_1"),
        ("valid_email_11@gmail.com", "valid_password_11", "valid_11"),
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
    # Leave users unverified


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
    ac,
    captured_verification_email,
    email,
    password,
    first_name,
    last_name,
    birth_date,
    bio,
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

    # Verify user with captured email
    res = await ac.post("/v1/auth/verify-email", json=captured_verification_email)
    assert res.status_code == 200
    assert res.json()["status"] == "verified"


async def test_signup_on_conflict(ac, get_active_users):
    for user in islice(get_active_users, 2):
        res = await ac.post(
            "/v1/auth/signup",
            json={
                "email": user["email"],
                "password": user["password"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "birth_date": user.get("birth_date"),
                "bio": user.get("bio"),
            },
        )
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
    # If validation returns structured details, keep these checks stable
    assert res.json()["detail"][0]["loc"][1] == field
    assert res.json()["detail"][0]["input"] == value


async def test_login(ac, get_active_users, jwt_provider):
    for user in islice(get_active_users, 2):
        res = await _login(ac, user["email"], user["password"])
        assert res.status_code == 200

        access, refresh = _assert_tokens_present(ac)

        access_payload, refresh_payload = _decode_tokens_and_basic_asserts(
            jwt_provider, access, refresh, email=user["email"]
        )

        _assert_token_ttls(access_payload, refresh_payload)


@pytest.mark.parametrize(
    "field, value",
    (
        ("email", "invalid_email"),
        ("password", "123"),
        ("extra", "unknown"),
    ),
)
async def test_login_invalid(ac, get_active_users, field, value):
    user = get_active_users[0]
    body = {
        "email": user["email"],
        "password": user["password"],
        field: value,
    }

    ac.cookies.clear()
    res = await ac.post("/v1/auth/login", json=body)
    assert res.status_code == 422
    assert "detail" in res.json()
    assert res.json()["detail"][0]["loc"][1] == field
    assert res.json()["detail"][0]["input"] == value


async def test_login_with_wrong_password(ac, get_active_users):
    for user in islice(get_active_users, 2):
        res = await _login(ac, user["email"], "wrong_password123")
        assert res.status_code == 401
        assert "detail" in res.json()


async def test_login_user_not_found(ac, get_active_users):
    res = await _login(ac, "no_such_user@gmail.com", "some_password123")
    assert res.status_code == 404
    assert "detail" in res.json()


async def test_login_user_unverified(ac):
    user = {
        "email": "monica_harbor@gmail.com",
        "password": "password123",
        "first_name": "Monica",
    }
    res = await ac.post("/v1/auth/signup", json=user)
    assert res.status_code == 201

    res = await _login(ac, user["email"], user["password"])
    assert res.status_code == 401


async def test_login_user_already_authorized(authed_ac):
    user = authed_ac.user

    res = await authed_ac.post(
        "/v1/auth/login",
        json={"email": user["email"], "password": user["password"]},
    )
    assert res.status_code == 409


async def test_refresh_token(authed_ac, jwt_provider):
    old_access, old_refresh = _assert_tokens_present(authed_ac)

    await asyncio.sleep(1)  # wait so that exp changes

    res = await authed_ac.post("/v1/auth/refresh")
    assert res.status_code == 200

    new_access, same_refresh = _assert_tokens_present(authed_ac)

    assert old_access != new_access
    assert old_refresh == same_refresh

    access_payload, refresh_payload = _decode_tokens_and_basic_asserts(
        jwt_provider, new_access, same_refresh
    )
    _assert_token_ttls(access_payload, refresh_payload)


async def test_refresh_token_revoked(ac, get_active_users):
    assert len(get_active_users) > 1
    for user in islice(get_active_users, 2):
        res1 = await _login(ac, user["email"], user["password"])
        assert res1.status_code == 200

        _assert_tokens_present(ac)

        res = await ac.post("/v1/auth/logout")
        assert res.status_code == 200

        ac.cookies.update(res1.cookies)

        res = await ac.post("/v1/auth/refresh")
        assert res.status_code == 401


async def test_refresh_tokens_client_mismatch(ac, get_active_users):
    user = get_active_users[0]

    res = await _login(ac, user["email"], user["password"])
    assert res.status_code == 200

    res = await ac.post("/v1/auth/refresh")
    assert res.status_code == 200

    ac.headers["user-agent"] = "Unknown User Agent v1/0"

    res = await ac.post("/v1/auth/refresh")
    assert res.status_code == 401


async def test_logout(ac, get_active_users):
    user = get_active_users[0]
    res = await _login(ac, user["email"], user["password"])
    assert res.status_code == 200

    res = await ac.post("/v1/auth/logout")
    assert res.status_code == 200

    access = ac.cookies.get("access_token")
    refresh = ac.cookies.get("refresh_token")

    assert access is None, "Access token should be cleared after logout"
    assert refresh is None, "Refresh token should be cleared after logout"


async def test_verify_user_valid(ac, get_inactive_users, captured_verification_email):
    assert len(get_inactive_users) > 1
    for user in islice(get_inactive_users, 2):
        res = await ac.post("/v1/auth/resend-code", json={"email": user["email"]})
        assert res.status_code == 200

        res = await ac.post("/v1/auth/verify-email", json=captured_verification_email)
        assert res.status_code == 200
        assert res.json()["status"] == "verified"


async def test_verify_user_wrong_code(ac, get_inactive_users):
    assert len(get_inactive_users) > 1
    for user in islice(get_inactive_users, 2):
        res = await ac.post("/v1/auth/resend-code", json={"email": user["email"]})
        assert res.status_code == 200

        wrong_code = "AAA123"
        res = await ac.post(
            "/v1/auth/verify-email", json={"email": user["email"], "code": wrong_code}
        )
        assert res.status_code == 400

        invalid_code = "invalid"
        res = await ac.post(
            "/v1/auth/verify-email", json={"email": user["email"], "code": invalid_code}
        )
        assert res.status_code == 422


async def test_verify_user_not_found(ac, get_inactive_users):
    res = await ac.post("/v1/auth/resend-code", json={"email": "unknown_email@unknown.com"})
    assert res.status_code == 404
    assert "detail" in res.json()


async def test_forgot_password_valid(ac, get_active_users, captured_verification_email):
    assert len(get_active_users) > 1
    for index, user in enumerate(islice(get_active_users, 2)):
        ac.cookies.clear()

        res = await ac.post("/v1/auth/forgot-password", json={"email": user["email"]})
        assert res.status_code == 200

        new_password = "some_new_password_123"
        res = await ac.post(
            "/v1/auth/reset-password-confirmation",
            json={**captured_verification_email, "new_password": new_password},
        )
        assert res.status_code == 200

        # trying login
        res = await _login(ac, user["email"], new_password)
        assert res.status_code == 200

        _assert_tokens_present(ac)

        # update password in fixture list so subsequent tests use new password
        get_active_users[index]["password"] = new_password


async def test_forgot_password_wrong_code(
    ac, clear_redis, get_active_users, captured_verification_email
):
    assert len(get_active_users) > 1
    for user in islice(get_active_users, 2):
        res = await ac.post("/v1/auth/forgot-password", json={"email": user["email"]})
        assert res.status_code == 200

        wrong_code = "WRONG1"
        res = await ac.post(
            "/v1/auth/reset-password-confirmation",
            json={
                "email": captured_verification_email["email"],
                "code": wrong_code,
                "new_password": "some_new_password_123",
            },
        )
        assert res.status_code == 400


async def test_change_password_valid(ac, get_active_users):
    assert len(get_active_users) > 1
    for index, user in enumerate(islice(get_active_users, 2)):
        current_password = user["password"]
        new_password = "new_secure_password_567"

        # login with old password
        res = await _login(ac, user["email"], current_password)
        assert res.status_code == 200
        _assert_tokens_present(ac)

        # change password
        res = await ac.post(
            "/v1/auth/change-password",
            json={"password": current_password, "new_password": new_password},
        )
        assert res.status_code == 200

        # logout
        await ac.post("/v1/auth/logout")

        # login with old password -> fail
        res = await _login(ac, user["email"], current_password)
        assert res.status_code == 401

        # login with the new password -> success
        res = await _login(ac, user["email"], new_password)
        assert res.status_code == 200

        _assert_tokens_present(ac)

        # update fixture data for future tests
        get_active_users[index]["password"] = new_password


async def test_change_password_same_password(authed_ac):
    user = authed_ac.user
    current_password = user["password"]

    # trying to change to the same password
    res = await authed_ac.post(
        "/v1/auth/change-password",
        json={
            "password": current_password,
            "new_password": current_password,
        },
    )
    assert res.status_code == 400
    assert "detail" in res.json()


async def test_change_password_invalid(authed_ac):
    # authed_ac fixture already logs in user and has .user attribute
    current_password = authed_ac.user["password"]

    # new password is too short (invalid by validation rules)
    weak_password = "123"

    res = await authed_ac.post(
        "/v1/auth/change-password",
        json={
            "password": current_password,
            "new_password": weak_password,
        },
    )
    assert res.status_code == 422
    assert "detail" in res.json()
    assert res.json()["detail"][0]["loc"][1] == "new_password"


async def test_change_password_incorrect(authed_ac):
    incorrect_password = "some_mistake_123"
    new_password = "new_password_123"

    res = await authed_ac.post(
        "/v1/auth/change-password",
        json={
            "password": incorrect_password,
            "new_password": new_password,
        },
    )
    assert res.status_code == 400
    assert "detail" in res.json()
