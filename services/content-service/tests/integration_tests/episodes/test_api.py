import pytest


@pytest.mark.parametrize(
    "title, episode_number, duration, status_code, video_url",
    [
        # Valid data
        ("Title is Valid", 1, 22, 201, None),
        ("Title is Valid", 2, 22, 201, None),
        ("Title is Valid", 3, 22, 201, "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        # Invalid episode number
        ("Title is Valid", 10000, 22, 422, None),
        ("Title is Valid", -1, 22, 422, None),
        # Invalid duration
        ("Title is Valid", 4, -1, 422, None),
        ("Title is Valid", 5, 10000, 422, None),
        # Invalid URL
        ("Title is Valid", 4, 22, 422, "invalid_uri_link"),
        # Invalid title
        ("A", 5, 22, 422, None),
        ("Aa", 5, 22, 422, None),
        ("A"*256, 5, 22, 422, None),
        # Conflict
        # URI
        ("Title is Valid", 11, 22, 409, "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        # Episode number
        ("Title is Valid", 1, 22, 409, None),
    ]
)
async def test_add_episode(
    ac,
    get_series_and_season_ids,
    title,
    episode_number,
    duration,
    status_code,
    video_url,
):
    series_id, season_id = get_series_and_season_ids
    req_json = {
        "series_id": series_id,
        "season_id": season_id,
        "title": title,
        "episode_number": episode_number,
        "duration": duration,
        "video_url": video_url,
    }
    res = await ac.post(f"/episodes", json=req_json)
    assert res.status_code == status_code
