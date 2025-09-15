from itertools import islice

import pytest
from uuid_extensions import uuid7str

from tests.utils import get_and_validate, calculate_expected_length


async def test_actors_pagination(ac, get_all_actors):
    per_page = 3
    for page in range(1, 10):
        expected_length = calculate_expected_length(page, per_page, len(get_all_actors))
        data = await get_and_validate(
            ac=ac,
            url="/v1/actors",
            params={
                "page": page,
                "per_page": per_page,
            },
        )
        assert len(data) == expected_length


async def test_get_actor(ac, get_all_actors):
    for actor in islice(get_all_actors, 2):
        data = await get_and_validate(
            ac=ac,
            url=f"/v1/actors/{actor['id']}",
            expect_list=False,
        )
        assert isinstance(data, dict)
        assert data["id"] == actor["id"]
        assert data["first_name"] == actor["first_name"]
        assert data["last_name"] == actor["last_name"]
        assert data["birth_date"] == actor["birth_date"]
        assert data["zodiac_sign"] == actor["zodiac_sign"]
        assert data["bio"] == actor["bio"]
        assert data["created_at"] == actor["created_at"]
        assert data["updated_at"] == actor["updated_at"]


async def test_get_actor_not_found(ac):
    res = await ac.get(f"/v1/actors/{uuid7str()}")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.parametrize(
    "first_name, last_name, birth_date, zodiac_sign, bio",
    [
        ("John", "Smith", "1977-01-17", None, None),
        ("Lana", "Light", "1988-01-25", "Pisces", "Well-known actress"),
    ],
)
async def test_add_actor_valid(ac, first_name, last_name, birth_date, zodiac_sign, bio):
    req_body = {
        "first_name": first_name,
        "last_name": last_name,
        "birth_date": birth_date,
        "zodiac_sign": zodiac_sign,
        "bio": bio,
    }
    res = await ac.post("/v1/actors", json=req_body)
    assert res.status_code == 201

    actor_id = res.json()["data"]["id"]

    added_actor = await get_and_validate(
        ac=ac,
        url=f"/v1/actors/{actor_id}",
        expect_list=False,
    )
    assert added_actor["id"] == actor_id
    assert added_actor["first_name"] == first_name
    assert added_actor["last_name"] == last_name
    assert added_actor["birth_date"] == birth_date
    assert added_actor["zodiac_sign"] == zodiac_sign
    assert added_actor["bio"] == bio
    assert added_actor["created_at"]
    assert added_actor["updated_at"]


@pytest.mark.parametrize(
    "field, value",
    (
        ("first_name", "f"),
        ("first_name", "f" * 50),
        ("last_name", "l"),
        ("last_name", "l" * 50),
        ("birth_date", "999-01-01"),
        ("birth_date", "2100-01-01"),
        ("zodiac_sign", "unknown"),
        ("bio", "b"),
        ("bio", "b" * 1025),
        ("extra", "unknown"),
    ),
)
async def test_add_actor_invalid(ac, field, value):
    data = {
        "first_name": "Test1",
        "last_name": "Test1",
        "birth_date": "1955-01-01",
        "zodiac_sign": "Pisces",
        "bio": "Likes kittens...",
        field: value,
    }
    res = await ac.post("/v1/actors", json=data)
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_add_actor_on_conflict(ac, get_all_actors):
    actor = get_all_actors[0]
    res = await ac.post(
        "/v1/actors",
        json={
            "first_name": actor["first_name"],
            "last_name": actor["last_name"],
            "birth_date": actor["birth_date"],
        },
    )
    assert res.status_code == 409
    assert "detail" in res.json()


@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", "Updated first name"),
        ("last_name", "Updated last name"),
        ("birth_date", "1957-01-01"),
        ("zodiac_sign", "Capricorn"),
        ("bio", "Updated bio ... "),
    ],
)
async def test_update_actor_valid(ac, field, value, get_all_actors):
    actor = get_all_actors[0]

    res = await ac.patch(f"/v1/actors/{actor['id']}", json={field: value})
    assert res.status_code == 200

    updated_actor = await get_and_validate(
        ac=ac,
        url=f"/v1/actors/{actor['id']}",
        expect_list=False,
    )
    assert isinstance(updated_actor, dict)
    assert updated_actor["id"] == actor["id"]
    assert updated_actor[field] == value

    unchanged_fields = (
        "first_name",
        "last_name",
        "birth_date",
        "zodiac_sign",
        "bio",
    )
    for f in unchanged_fields:
        if f != field:
            assert updated_actor[f] == actor[f]

    assert updated_actor["created_at"] == actor["created_at"]
    assert updated_actor["updated_at"] != actor["updated_at"]


@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", "f"),
        ("first_name", "f" * 50),
        ("last_name", "l"),
        ("last_name", "l" * 50),
        ("birth_date", "999-01-01"),
        ("birth_date", "2100-01-01"),
        ("zodiac_sign", "unknown"),
        ("bio", "b"),
        ("bio", "b" * 1025),
        ("extra", "unknown"),
    ],
)
async def test_update_actor_invalid(ac, field, value, get_all_actors):
    actor_id = get_all_actors[0]["id"]
    res = await ac.patch(f"/v1/actors/{actor_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_update_actor_not_found(ac):
    res = await ac.patch(f"/v1/actors/{uuid7str()}", json={"first_name": "Willa"})
    assert res.status_code == 404
    assert "detail" in res.json()


async def test_update_actor_on_conflict(ac, get_all_actors):
    actor_1, actor_2 = get_all_actors[:2]

    res = await ac.patch(
        url=f"/v1/actors/{actor_1['id']}",
        json={
            "first_name": actor_2["first_name"],
            "last_name": actor_2["last_name"],
            "birth_date": actor_2["birth_date"],
        },
    )
    assert res.status_code == 409
    assert "detail" in res.json()


async def test_delete_actor(ac, get_all_actors):
    for actor in islice(get_all_actors, 2):
        assert (await ac.get(f"/v1/actors/{actor['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/actors/{actor['id']}")).status_code == 204
        assert (await ac.get(f"/v1/actors/{actor['id']}")).status_code == 404
