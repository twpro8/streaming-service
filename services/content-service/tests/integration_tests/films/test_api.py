from datetime import date

import pytest


async def test_get_films(ac):
    res = await ac.get("/films")
    assert isinstance(res.json()["data"], list)
    assert res.status_code == 200


@pytest.mark.parametrize(
    "title, description, director, release_year, duration, cover_url, status_code",
    [
        # Valid data - should succeed
        (
            "Inception",
            "A mind-bending thriller",
            "Christopher Nolan",
            "2010-07-16",
            148,
            "https://example.com/inception.jpg",
            201,
        ),
        # Empty title - should fail validation
        ("", "Some description", "Director Name", "2020-01-01", 100, None, 422),
        # Very long title - should fail validation
        ("T" * 300, "Desc", "Director", "2020-01-01", 90, None, 422),
        # release_year in the future - should fail validation
        # ("Future Film", "Desc", "Dir", "2100-01-01", 90, None, 422),
        # Negative duration - should fail validation
        ("Film", "Desc", "Director", "2020-01-01", -10, None, 422),
        # Excessively long duration - should fail validation
        ("Long Film", "Description", "Director", "2020-01-01", 10000, None, 422),
        # Invalid cover_url format - should fail validation
        ("Film", "Description", "Director", "2020-01-01", 90, "not-a-url", 422),
        # Empty director - should fail validation
        ("Film", "Description", "", "2020-01-01", 90, None, 422),
        # All optional fields None (cover_url) - should succeed
        ("Film", "Description", "Dir", "2020-01-01", 90, None, 201),
    ],
)
async def test_add_film(
    ac,
    title: str,
    description: str,
    director: str,
    release_year: date,
    duration: int,
    cover_url: str,
    status_code: int,
):
    request_json = {
        "title": title,
        "description": description,
        "director": director,
        "release_year": release_year,
        "duration": duration,
        "cover_url": cover_url,
    }
    res = await ac.post("/films", json=request_json)
    assert res.status_code == status_code


@pytest.mark.parametrize(
    "title, description, director, release_year, duration, cover_url, video_url, status_code",
    [
        # Valid full update - all fields set correctly
        (
            "Interstellar",
            "Space exploration epic",
            "Christopher Nolan",
            "2014-11-07",
            169,
            "https://example.com/interstellar.jpg",
            "https://cdn.example.com/video1.mp4",
            200,
        ),
        # Empty title - invalid
        ("", "No title", "Director", "2020-01-01", 100, None, None, 422),
        # Too long title - invalid
        ("X" * 256, "Long title", "Director", "2020-01-01", 90, None, None, 422),
        # Future release year - invalid
        ("Future Movie", "Desc", "Director", "2100-01-01", 100, None, None, 422),
        # Negative duration - invalid
        ("Bad Duration", "Desc", "Director", "2020-01-01", -50, None, None, 422),
        # Excessive duration - invalid
        ("Too Long", "Desc", "Director", "2020-01-01", 10000, None, None, 422),
        # Invalid cover_url format - invalid
        ("Invalid URL", "Desc", "Director", "2020-01-01", 90, "not-a-url", None, 422),
        # Valid update with null cover and video
        ("Minimal", "Just enough", "Someone", "2015-03-03", 88, None, None, 200),
        # Empty director - invalid
        ("Nameless", "Good movie", "", "2020-01-01", 90, None, None, 422),
        # Invalid video_url format - invalid
        ("Bad Video URL", "Test", "Test Director", "2020-01-01", 90, None, "not-a-video-url", 422),
        # Valid video_url provided
        (
            "Video Ready",
            "Has video link",
            "Test Director",
            "2021-06-06",
            100,
            "https://example.com/cover.jpg",
            "https://cdn.example.com/video.mp4",
            200,
        ),
        # cover_url and video_url both null - valid
        ("No Media", "Just text.", "Director", "2010-10-10", 95, None, None, 200),
        # cover_url valid, video_url null - valid
        (
            "Cover Only",
            "Visuals only",
            "Director",
            "2018-08-08",
            110,
            "https://example.com/cover2.jpg",
            None,
            200,
        ),
        # cover_url null, video_url valid - valid
        (
            "Streamable",
            "Only online",
            "Director",
            "2019-09-09",
            105,
            None,
            "https://cdn.example.com/stream.mp4",
            200,
        ),
    ],
)
async def test_replace_film(
    ac,
    title: str,
    description: str,
    director: str,
    release_year: str,
    duration: int,
    cover_url: str,
    video_url: str,
    status_code: int,
):
    request_json = {
        "title": title,
        "description": description,
        "director": director,
        "release_year": release_year,
        "duration": duration,
        "cover_url": cover_url,
        "video_url": video_url,
    }

    res = await ac.get("/films")
    film_id = res.json()["data"][-1]["id"]
    res = await ac.put(f"/films/{film_id}", json=request_json)
    assert res.status_code == status_code


@pytest.mark.parametrize(
    "update_data, status_code",
    [
        # Update title only
        ({"title": "Updated Title"}, 200),
        # Update description only
        ({"description": "New description of the film."}, 200),
        # Update director only
        ({"director": "Updated Director"}, 200),
        # Update release_year only
        ({"release_year": "2021-01-01"}, 200),
        # Update duration only
        ({"duration": 120}, 200),
        # Update cover_url only
        ({"cover_url": "https://example.com/updated.jpg"}, 200),
        # Update video_url only
        ({"video_url": "https://cdn.example.com/newvideo.mp4"}, 200),
        # Update multiple fields
        ({"title": "New Title", "description": "New Description", "duration": 99}, 200),
        # Invalid duration (negative)
        ({"duration": -10}, 422),
        # Invalid release_year (future date)
        # ({"release_year": "2100-01-01"}, 422),
        # Invalid cover_url
        ({"cover_url": "not-a-valid-url"}, 422),
        # Invalid video_url
        ({"video_url": "bad-url"}, 422),
        # Empty title — should fail if not allowed
        ({"title": ""}, 422),
        # Empty director — should fail
        ({"director": ""}, 422),
        # Nullify optional fields
        ({"cover_url": None, "video_url": None}, 200),
    ],
)
async def test_patch_film(
    ac,
    update_data: dict,
    status_code: int,
):
    res = await ac.get("/films")
    film_id = res.json()["data"][-2]["id"]
    response = await ac.patch(f"/films/{film_id}", json=update_data)
    assert response.status_code == status_code


async def test_delete_film(ac):
    res = await ac.get("/films")
    film_id = res.json()["data"][-1]["id"]

    res = await ac.delete(f"/films/{film_id}")
    assert res.status_code == 204

    res = await ac.get(f"/films/{film_id}")
    assert res.status_code == 404
