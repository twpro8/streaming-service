import pytest
from math import ceil


@pytest.fixture
async def created_genres(ac):
    ids = []
    for name in ["TestGenre1", "TestGenre2", "TestGenre3"]:
        res = await ac.post("/genres", json={"name": name})
        assert res.status_code == 201
        ids.append(res.json()["data"]["id"])
    yield ids
    for genre_id in ids:
        await ac.delete(f"/genres/{genre_id}")


@pytest.mark.parametrize(
    "params",
    [
        {"page": 1, "per_page": 3},
        {"page": 2, "per_page": 3},
        {"page": 3, "per_page": 3},
        {"page": 4, "per_page": 3},
        {"page": 1, "per_page": 30},
    ],
)
async def test_get_genres(ac, params):
    all_res = await ac.get("/genres", params={"page": 1, "per_page": 30})
    assert all_res.status_code == 200
    all_genres = all_res.json()["data"]
    total_count = len(all_genres)

    res = await ac.get("/genres", params=params)
    assert res.status_code == 200

    data = res.json()["data"]

    page = params["page"]
    per_page = params["per_page"]
    total_pages = ceil(total_count / per_page)

    if page <= total_pages:
        expected_length = min(per_page, total_count - (page - 1) * per_page)
    else:
        expected_length = 0

    assert len(data) == expected_length

    for item in data:
        assert isinstance(item["id"], int)
        assert isinstance(item["name"], str)


async def test_get_existing_genre(ac, created_genres):
    for genre_id in created_genres:
        res = await ac.get(f"/genres/{genre_id}")
        assert res.status_code == 200
        assert res.json()["data"]["id"] == genre_id


async def test_get_nonexistent_genre(ac):
    res = await ac.get("/genres/999999")
    assert res.status_code == 404


@pytest.mark.parametrize("name", ["Valid1", "Valid2", "Valid4"])
async def test_add_genre_valid(ac, name):
    res = await ac.post("/genres", json={"name": "TempGenre"})
    assert res.status_code == 201
    genre_id = res.json()["data"]["id"]

    res = await ac.get(f"/genres/{genre_id}")
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "TempGenre"

    await ac.delete(f"/genres/{genre_id}")


@pytest.mark.parametrize("name", ["N" * 50, "N", 1, False])
async def test_add_genre_invalid(ac, name):
    res = await ac.post("/genres", json={"name": name})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_delete_genre(ac, created_genres):
    for genre_id in created_genres:
        assert (await ac.get(f"/genres/{genre_id}")).status_code == 200
        assert (await ac.delete(f"/genres/{genre_id}")).status_code == 204
        assert (await ac.get(f"/genres/{genre_id}")).status_code == 404
