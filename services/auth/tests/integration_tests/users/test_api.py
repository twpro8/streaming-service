import pytest


async def test_get_me(authed_ac):
    res = await authed_ac.get("/v1/users/me")
    assert res.status_code == 200


@pytest.mark.parametrize(
    "user_data",
    (
        {
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1985-07-09",
            "bio": "Python Backend Dev",
            "picture_url": "https://jogn-doe.com/pics/342",
        },
        {
            "first_name": "Steven",
            "last_name": "King",
            "birth_date": "1974-08-04",
            "bio": "Researcher from Poland",
            "picture_url": "https://sv-king.com/pics/867",
        },
    ),
)
async def test_update_user_valid(authed_ac, user_data):
    res = await authed_ac.patch("/v1/users", json=user_data)
    assert res.status_code == 200

    res = await authed_ac.get("/v1/users/me")
    assert res.status_code == 200

    new_user = res.json().get("data")

    assert new_user is not None
    assert new_user["first_name"] == user_data["first_name"]
    assert new_user["last_name"] == user_data["last_name"]
    assert new_user["birth_date"] == user_data["birth_date"]
    assert new_user["bio"] == user_data["bio"]
    assert new_user["picture"] == user_data["picture_url"]


@pytest.mark.parametrize(
    "field, value",
    (
        ("first_name", "f"),
        ("first_name", "f" * 49),
        ("last_name", "l"),
        ("last_name", "l" * 49),
        ("birth_date", "invalid date"),
        ("birth_date", "1500-01-01"),
        ("birth_date", "2200-01-01"),
        ("bio", "b"),
        ("bio", "b" * 1025),
        ("picture_url", "invalid_url"),
        ("extra", "unknown"),
    ),
)
async def test_update_user_invalid(authed_ac, field, value):
    user_data = {
        "first_name": "Sven",
        "last_name": "Joystick",
        "birth_date": "1964-08-04",
        "bio": "I am just a girl.",
        "picture_url": "https://sv-joy.com/pics/423",
        field: value,
    }
    res = await authed_ac.patch("/v1/users", json=user_data)
    assert res.status_code == 422
    assert res.json()["detail"][0]["loc"][1] == field
    assert res.json()["detail"][0]["input"] == value


async def test_delete_user(authed_ac):
    res = await authed_ac.delete("/v1/users")
    assert res.status_code == 204

    res = await authed_ac.get("/v1/users/me")
    assert res.status_code == 400
