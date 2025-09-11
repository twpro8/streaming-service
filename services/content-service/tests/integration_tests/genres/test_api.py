from itertools import islice

import pytest

from tests.utils import calculate_expected_length, get_and_validate


async def test_get_genres(ac, get_all_genres):
    per_page = 3
    for page in range(1, 7):
        data = await get_and_validate(
            ac=ac,
            url="/v1/genres",
            params={
                "page": page,
                "per_page": per_page,
            },
        )
        expected_length = calculate_expected_length(page, per_page, len(get_all_genres))
        assert len(data) == expected_length
        for item in data:
            assert isinstance(item["id"], int)
            assert isinstance(item["name"], str)


async def test_get_genre(ac, get_all_genres):
    for genre in islice(get_all_genres, 2):
        data = await get_and_validate(
            ac=ac,
            url=f"/v1/genres/{genre['id']}",
            expect_list=False,
        )
        assert isinstance(data, dict)
        assert data["id"] == genre["id"]
        assert data["name"] == genre["name"]


async def test_get_genre_not_found(ac):
    res = await ac.get("/v1/genres/999999")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.parametrize("name", ["Valid1", "Valid2", "Valid4"])
async def test_add_genre_valid(ac, name):
    res = await ac.post("/v1/genres", json={"name": name})
    assert res.status_code == 201

    genre_id = res.json()["data"]["id"]
    added_genre = await get_and_validate(
        ac=ac,
        url=f"/v1/genres/{genre_id}",
        expect_list=False,
    )
    assert isinstance(added_genre, dict)
    assert added_genre["id"] == genre_id
    assert added_genre["name"] == name


@pytest.mark.parametrize("name", ["N" * 50, "N"])
async def test_add_genre_invalid(ac, name):
    res = await ac.post("/v1/genres", json={"name": name})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_add_genre_on_conflict(ac, get_all_genres):
    for genre in islice(get_all_genres, 2):
        res = await ac.post("/v1/genres", json={"name": genre["name"]})
        assert res.status_code == 409
        assert "detail" in res.json()


async def test_delete_genre(ac, created_genres):
    for genre_id in created_genres:
        assert (await ac.get(f"/v1/genres/{genre_id}")).status_code == 200
        assert (await ac.delete(f"/v1/genres/{genre_id}")).status_code == 204
        assert (await ac.get(f"/v1/genres/{genre_id}")).status_code == 404
