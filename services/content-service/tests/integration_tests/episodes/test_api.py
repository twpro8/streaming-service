import pytest


@pytest.mark.parametrize(
    "params, target_length",
    [
        ({"page": 1, "per_page": 30}, 20),
        ({"page": 1, "per_page": 5}, 5),
        ({"page": 2, "per_page": 5}, 5),
        ({"page": 3, "per_page": 5}, 5),
        ({"page": 4, "per_page": 5}, 5),
        ({"page": 5, "per_page": 5}, 0),
        ({"title": "Serial 1", "page": 1, "per_page": 30}, 4),
        ({"title": "Serial 2", "page": 1, "per_page": 30}, 4),
        ({"title": "Serial 3", "page": 1, "per_page": 30}, 4),
        ({"title": "Serial 4", "page": 1, "per_page": 30}, 4),
        ({"title": "Serial 5", "page": 1, "per_page": 30}, 4),
        ({"title": "Season 1", "page": 1, "per_page": 30}, 10),
        ({"title": "Season 2", "page": 1, "per_page": 30}, 10),
        ({"title": "Episode 1", "page": 1, "per_page": 30}, 10),
        ({"title": "Episode 2", "page": 1, "per_page": 30}, 10),
        ({"episode_number": 1, "page": 1, "per_page": 30}, 10),
        ({"episode_number": 2, "page": 1, "per_page": 30}, 10),
        ({"series_id": "bf5315e1-fdfc-4af3-b18c-1ccc83892797"}, 4),
        ({"series_id": "ef66e5c2-0931-4c43-bb6d-bb2b2ec3c9c4"}, 4),
        ({"series_id": "ecc3631e-fc14-4fe3-b547-155b30045d6d"}, 4),
        ({"series_id": "49f7cbdb-ec47-4807-8ed4-dc78d206a9ad"}, 4),
        ({"series_id": "bf7264e9-6e93-424a-a1f5-943b55f1e102"}, 4),
        ({"season_id": "d5ed6e69-5d07-474f-81e4-86627a576d45"}, 2),
        ({"season_id": "81c29ee1-db3e-4d81-a257-d05e29773deb"}, 2),
        ({"season_id": "abb704d5-da18-4d6a-942e-58f1b6172109"}, 2),
        ({"season_id": "99edd9cc-cd08-4a9d-8809-93b86ab06d28"}, 2),
        ({"season_id": "00200739-4730-42ac-8a5a-bad5112558ee"}, 2),
        ({"season_id": "839e3c16-f646-4d3e-a23a-28767330e753"}, 2),
        ({"season_id": "e6220848-9b53-4c62-bd58-96f07e3cf15a"}, 2),
        ({"season_id": "1ed127d0-d7f6-4bd3-936b-7c47c6acee01"}, 2),
        ({"season_id": "a1970665-0eb4-4375-a569-6c6ed71ba58c"}, 2),
        ({"season_id": "5fb8260f-3c43-436b-a264-ca37aa931a9c"}, 2),
    ],
)
async def test_get_episodes(ac, params, target_length):
    res = await ac.get("/episodes", params=params)
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == target_length


@pytest.mark.parametrize(
    "title, episode_number, duration, video_url, status_code, series_id, season_id",
    [
        # Valid data
        (
            "Serial 1 Season 1 Episode 3 Added",
            3,
            40,
            "https://www.youtube.com/watch?v=p00EF6_b5pI",
            201,
            None,
            None,
        ),
        (
            "Serial 1 Season 1 Episode 4 Added",
            4,
            40,
            "https://www.youtube.com/watch?v=LpNVf8sczqU",
            201,
            None,
            None,
        ),
        # Invalid episode number
        ("Valid title", 10000, 40, None, 422, None, None),
        ("Valid title", -1, 40, None, 422, None, None),
        # # Invalid duration
        ("Valid title", 5, -1, None, 422, None, None),
        ("Valid title", 6, 10000, None, 422, None, None),
        # Invalid title
        ("A", 5, 40, None, 422, None, None),
        ("Aa", 5, 40, None, 422, None, None),
        ("A" * 256, 5, 40, None, 422, None, None),
        # Invalid URI
        ("Valid title", 5, 40, "invalid-uri", 422, None, None),
        # Conflict
        ("Valid title", 1, 40, None, 409, None, None),
        ("Valid title", 2, 40, None, 409, None, None),
        ("Valid title", 3, 40, None, 409, None, None),
        ("Valid title", 4, 40, None, 409, None, None),
        ("Valid title", 9, 40, "https://www.youtube.com/watch?v=p00EF6_b5pI", 409, None, None),
        # Series not found
        ("Valid title", 10, 40, None, 404, "d5ed6e69-5d07-474f-81e4-86627a576d45", None),
        # Season not found
        ("Valid title", 11, 40, None, 404, None, "bf5315e1-fdfc-4af3-b18c-1ccc83892797"),
    ],
)
async def test_add_episode(
    ac,
    title,
    episode_number,
    duration,
    video_url,
    status_code,
    series_id,
    season_id,
):
    series_id = series_id or "bf5315e1-fdfc-4af3-b18c-1ccc83892797"
    season_id = season_id or "d5ed6e69-5d07-474f-81e4-86627a576d45"
    req_json = {
        "series_id": series_id,
        "season_id": season_id,
        "title": title,
        "episode_number": episode_number,
        "duration": duration,
        "video_url": video_url,
    }
    res = await ac.post("/episodes", json=req_json)
    assert res.status_code == status_code


@pytest.mark.parametrize(
    "patch_data, expected_status, episode_id",
    [
        # Valid data
        ({"title": "Serial 1 Season 1 Episode 1 Updated"}, 200, None),
        ({"duration": 110}, 200, None),
        ({"episode_number": 10}, 200, None),
        ({"video_url": "https://www.youtube.com/watch?v=vGVeDm4118Q"}, 200, None),
        (
            {"title": "Serial 1 Season 1 Episode 2 Updated"},
            200,
            "d2d887fa-ac59-4be1-b92e-eb1fb0d4260f",
        ),
        ({"duration": 110}, 200, "d2d887fa-ac59-4be1-b92e-eb1fb0d4260f"),
        ({"episode_number": 11}, 200, "d2d887fa-ac59-4be1-b92e-eb1fb0d4260f"),
        (
            {"video_url": "https://www.youtube.com/watch?v=4FIMsKKvBRM"},
            200,
            "d2d887fa-ac59-4be1-b92e-eb1fb0d4260f",
        ),
        # All fields None
        (
            {
                "title": None,
                "episode_number": None,
                "duration": None,
                "video_url": None,
            },
            422,
            None,
        ),
        # Invalid title
        ({"title": "A"}, 422, None),
        ({"title": "Aa"}, 422, None),
        ({"title": "A" * 256}, 422, None),
        # Invalid episode number
        ({"episode_number": 10000}, 422, None),
        ({"episode_number": -1}, 422, None),
        ({"episode_number": None}, 422, None),
        ({"episode_number": ""}, 422, None),
        # Invalid duration
        ({"duration": 10000}, 422, None),
        ({"duration": -1}, 422, None),
        ({"duration": ""}, 422, None),
        ({"duration": None}, 422, None),
        # Invalid uri
        ({"video_url": "invalid-uri"}, 422, None),
        ({"video_url": ""}, 422, None),
        # Conflict
        ({"episode_number": 10}, 409, "d2d887fa-ac59-4be1-b92e-eb1fb0d4260f"),
        (
            {"video_url": "https://www.youtube.com/watch?v=vGVeDm4118Q"},
            409,
            "d2d887fa-ac59-4be1-b92e-eb1fb0d4260f",
        ),
    ],
)
async def test_update_episode(ac, patch_data, expected_status, episode_id):
    episode_id = episode_id or "36f863f9-616c-412e-8f48-e63d758cc9d0"
    res = await ac.patch(f"/episodes/{episode_id}", json=patch_data)
    assert res.status_code == expected_status


@pytest.mark.parametrize(
    "episode_id", ["fc865d9d-b06c-4907-916b-f7a04371c633", "89314656-ef19-4ae0-83bf-713149c94955"]
)
async def test_delete_episode(ac, episode_id):
    assert (await ac.get(f"/episodes/{episode_id}")).status_code == 200
    assert (await ac.delete(f"/episodes/{episode_id}")).status_code == 204
    assert (await ac.get(f"/episodes/{episode_id}")).status_code == 404
