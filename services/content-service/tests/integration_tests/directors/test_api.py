from itertools import islice

import pytest
from uuid_extensions import uuid7str

from tests.utils import get_and_validate, calculate_expected_length


async def test_directors_pagination(ac, get_all_directors):
    per_page = 3
    for page in range(1, 10):
        expected_length = calculate_expected_length(page, per_page, len(get_all_directors))
        data = await get_and_validate(
            ac=ac,
            url="/v1/directors",
            params={
                "page": page,
                "per_page": per_page,
            },
        )
        assert len(data) == expected_length


async def test_get_director(ac, get_all_directors):
    for director in islice(get_all_directors, 2):
        data = await get_and_validate(
            ac=ac,
            url=f"/v1/directors/{director['id']}",
            expect_list=False,
        )
        assert isinstance(data, dict)
        assert data["id"] == director["id"]
        assert data["first_name"] == director["first_name"]
        assert data["last_name"] == director["last_name"]
        assert data["birth_date"] == director["birth_date"]
        assert data["zodiac_sign"] == director["zodiac_sign"]
        assert data["bio"] == director["bio"]
        assert data["created_at"] == director["created_at"]
        assert data["updated_at"] == director["updated_at"]


async def test_get_director_not_found(ac):
    res = await ac.get(f"/v1/directors/{uuid7str()}")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.parametrize(
    "first_name, last_name, birth_date, zodiac_sign, bio",
    [
        ("John", "Smith", "1977-01-17", None, None),
        ("Lana", "Light", "1988-01-25", "Pisces", "Well-known director"),
    ],
)
async def test_add_director_valid(ac, first_name, last_name, birth_date, zodiac_sign, bio):
    req_body = {
        "first_name": first_name,
        "last_name": last_name,
        "birth_date": birth_date,
        "zodiac_sign": zodiac_sign,
        "bio": bio,
    }
    res = await ac.post("/v1/directors", json=req_body)
    assert res.status_code == 201

    director_id = res.json()["data"]["id"]

    added_director = await get_and_validate(
        ac=ac,
        url=f"/v1/directors/{director_id}",
        expect_list=False,
    )
    assert added_director["id"] == director_id
    assert added_director["first_name"] == first_name
    assert added_director["last_name"] == last_name
    assert added_director["birth_date"] == birth_date
    assert added_director["zodiac_sign"] == zodiac_sign
    assert added_director["bio"] == bio
    assert added_director["created_at"]
    assert added_director["updated_at"]


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
async def test_add_director_invalid(ac, field, value):
    req_body = {
        "first_name": "Add Test 1",
        "last_name": "Add Test 1",
        "birth_date": "1955-01-01",
        "zodiac_sign": "Pisces",
        "bio": "Likes kittens...",
        field: value,
    }
    res = await ac.post("/v1/directors", json=req_body)
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_add_director_on_conflict(ac, get_all_directors):
    director = get_all_directors[0]
    res = await ac.post(
        "/v1/directors",
        json={
            "first_name": director["first_name"],
            "last_name": director["last_name"],
            "birth_date": director["birth_date"],
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
async def test_update_director_valid(ac, field, value, get_all_directors):
    director = get_all_directors[0]

    res = await ac.patch(f"/v1/directors/{director['id']}", json={field: value})
    assert res.status_code == 200

    updated_director = await get_and_validate(
        ac=ac,
        url=f"/v1/directors/{director['id']}",
        expect_list=False,
    )
    assert isinstance(updated_director, dict)
    assert updated_director["id"] == director["id"]
    assert updated_director[field] == value

    unchanged_fields = (
        "first_name",
        "last_name",
        "birth_date",
        "zodiac_sign",
        "bio",
    )
    for f in unchanged_fields:
        if f != field:
            assert updated_director[f] == director[f]

    assert updated_director["created_at"] == director["created_at"]
    assert updated_director["updated_at"] == director["updated_at"]


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
async def test_update_director_invalid(ac, field, value, get_all_directors):
    director_id = get_all_directors[0]["id"]
    res = await ac.patch(f"/v1/directors/{director_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_update_director_not_found(ac):
    res = await ac.patch(f"/v1/directors/{uuid7str()}", json={"first_name": "Willa"})
    assert res.status_code == 404
    assert "detail" in res.json()


async def test_update_director_on_conflict(ac, get_all_directors):
    director_1, director_2 = get_all_directors[:2]

    res = await ac.patch(
        url=f"/v1/directors/{director_1['id']}",
        json={
            "first_name": director_2["first_name"],
            "last_name": director_2["last_name"],
            "birth_date": director_2["birth_date"],
        },
    )
    assert res.status_code == 409
    assert "detail" in res.json()


async def test_delete_director(ac, get_all_directors):
    for director in islice(get_all_directors, 2):
        assert (await ac.get(f"/v1/directors/{director['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/directors/{director['id']}")).status_code == 204
        assert (await ac.get(f"/v1/directors/{director['id']}")).status_code == 404
