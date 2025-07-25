from typing import List

import pytest


series_ids: List = []


async def test_get_series(ac):
    res = await ac.get("/series")

    global series_ids
    series_ids = [i["id"] for i in res.json()["data"]]

    assert len(series_ids) == 5
    assert res.status_code == 200


async def test_get_one_series(ac):
    for series_id in series_ids:
        res = await ac.get(f"/series/{series_id}")
        assert res.status_code == 200
        assert isinstance(res.json()["data"], dict)
        assert res.json()["data"]["id"] == series_id


@pytest.mark.parametrize(
    "title, description, director, release_year, cover_url, status_code",
    [
        # Valid data
        (
            "Neon Skies",
            "Sci-fi series set in a neon city",
            "Ava Bright",
            "2022-04-12",
            "https://example.com/neon.jpg",
            201,
        ),
        # Empty title — should fail
        ("", "Some description", "Director", "2020-01-01", None, 422),
        # Too long title — should fail
        ("T" * 300, "Desc", "Dir", "2020-01-01", None, 422),
        # Future release_year — should fail
        # ("Future Series", "Desc", "Dir", "2100-01-01", None, 422),
        # Invalid cover_url — should fail
        ("Bad URL", "Desc", "Dir", "2020-01-01", "not-a-url", 422),
        # Empty director — should fail
        ("Valid Title", "Desc", "", "2020-01-01", None, 422),
        # Valid with no cover_url — should succeed
        ("No Cover", "No cover provided", "Dir", "2020-01-01", None, 201),
        # Valid with full data — should succeed
        (
            "Full Set",
            "Complete info",
            "D. Creator",
            "2015-05-05",
            "https://example.com/cover.jpg",
            201,
        ),
        # release_year invalid format — should fail (if date parsing is strict)
        ("Bad Date", "Date issue", "Dir", "20-01-01", None, 422),
    ],
)
async def test_add_series(
    ac,
    title,
    description,
    director,
    release_year,
    cover_url,
    status_code,
):
    request_json = {
        "title": title,
        "description": description,
        "director": director,
        "release_year": release_year,
        "cover_url": cover_url,
    }
    res = await ac.post("/series", json=request_json)
    assert res.status_code == status_code

    if status_code == 201:
        added_series = res.json()["data"]

        assert added_series["title"] == title
        assert added_series["description"] == description
        assert added_series["director"] == director
        assert added_series["release_year"] == release_year
        assert added_series["cover_url"] == cover_url

        global series_ids
        series_ids.append(added_series["id"])


@pytest.mark.parametrize(
    "title, description, director, release_year, cover_url, status_code",
    [
        # Valid replacement — all fields correct
        (
            "Dark Horizons",
            "A noir crime drama",
            "Noah Lane",
            "2018-10-05",
            "https://example.com/dark.jpg",
            200,
        ),
        # Empty title — should fail
        ("", "Description here", "Some Director", "2019-01-01", None, 422),
        # Empty description — should fail
        ("Title", "", "Director", "2019-01-01", None, 422),
        # Empty director — should fail
        ("Title", "Desc", "", "2019-01-01", None, 422),
        # Valid with no cover_url
        ("No Image", "Minimal setup", "Creator", "2017-06-12", None, 200),
        # Future release_year — should fail
        # ("Time Traveler", "Too early", "Dir", "2099-01-01", None, 422),
        # Bad date format — should fail
        ("Bad Date", "Wrong date format", "Dir", "20-01-01", None, 422),
        # Invalid cover_url
        ("Bad URL", "Bad link", "Dir", "2020-01-01", "not-a-url", 422),
        # Valid with all fields filled
        (
            "The Climb",
            "Drama about mountaineering",
            "Sophie Hill",
            "2021-09-09",
            "https://example.com/climb.jpg",
            200,
        ),
        # Title too long
        ("T" * 300, "Normal desc", "Dir", "2020-01-01", None, 422),
        # Realistic modern show
        (
            "Urban Pulse",
            "A gritty urban story",
            "J. Smith",
            "2023-03-03",
            "https://example.com/pulse.jpg",
            200,
        ),
        # All fields empty — should fail
        ("", "", "", "", "", 422),
        # Missing cover_url with bad type (int instead of str or None)
        ("Title", "Desc", "Dir", "2020-01-01", 12345, 422),
        # Valid old show
        ("Classic Tales", "Old but gold", "Veteran Dir", "1990-05-20", None, 200),
    ],
)
async def test_replace_series(
    ac,
    title,
    description,
    director,
    release_year,
    cover_url,
    status_code,
):
    series_id = series_ids[-1]
    request_json = {
        "title": title,
        "description": description,
        "director": director,
        "release_year": release_year,
        "cover_url": cover_url,
    }
    res = await ac.put(f"/series/{series_id}", json=request_json)
    assert res.status_code == status_code


@pytest.mark.parametrize(
    "update_data, status_code",
    [
        # Update title only
        ({"title": "Renamed Show"}, 200),
        # Update description only
        ({"description": "Updated description for the series."}, 200),
        # Update director only
        ({"director": "New Director"}, 200),
        # Update release_year only
        ({"release_year": "2020-01-01"}, 200),
        # Update cover_url only
        ({"cover_url": "https://example.com/newcover.jpg"}, 200),
        # Update multiple fields
        (
            {
                "title": "New Title",
                "description": "Updated description",
                "director": "Director",
            },
            200,
        ),
        # Nullify optional cover_url
        ({"cover_url": None}, 200),
        # Empty title — should fail
        ({"title": ""}, 422),
        # Empty description — should fail
        ({"description": ""}, 422),
        # Empty director — should fail
        ({"director": ""}, 422),
        # Invalid release_year (future)
        # ({"release_year": "2100-01-01"}, 422),
        # Bad date format
        ({"release_year": "20-01-01"}, 422),
        # Bad URL in cover_url
        ({"cover_url": "not-a-url"}, 422),
        # cover_url with wrong type
        ({"cover_url": 123}, 422),
    ],
)
async def test_update_series(
    ac,
    update_data: dict,
    status_code: int,
):
    series_id = series_ids[-2]
    response = await ac.patch(f"/series/{series_id}", json=update_data)
    assert response.status_code == status_code


async def test_delete_series(ac):
    global series_ids

    for series_id in series_ids[:]:
        res = await ac.delete(f"/series/{series_id}")
        assert res.status_code == 204

        res = await ac.get(f"/series/{series_id}")
        assert res.status_code == 404

        series_ids.remove(series_id)

    assert len(series_ids) == 0
