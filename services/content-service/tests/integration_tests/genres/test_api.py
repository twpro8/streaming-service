import pytest

from tests.utils import calculate_expected_length


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
async def test_get_genres(ac, params, get_all_genres):
    res = await ac.get("/genres", params=params)
    assert res.status_code == 200

    data = res.json()["data"]

    expected_length = calculate_expected_length(
        params["page"], params["per_page"], len(get_all_genres)
    )

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
