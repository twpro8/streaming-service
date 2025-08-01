import pytest


films_ids = []


@pytest.mark.parametrize(
    "params, target_length",
    [
        ({"page": 1, "per_page": 30}, 5),
        ({"page": 1, "per_page": 2}, 2),
        ({"page": 2, "per_page": 2}, 2),
        ({"page": 3, "per_page": 2}, 1),
        # Exact title match
        ({"title": "Hidden"}, 1),
        ({"title": "Chamber"}, 1),
        # Director filter
        ({"director": "Greta Thorn"}, 1),
        ({"director": "Thorn Greta"}, 0),
        ({"director": "Guy"}, 1),
        # Description filter
        ({"description": "the"}, 2),
        ({"description": "about isolation"}, 1),
        ({"description": "post-apocalyptic wasteland"}, 1),
        # Exact release_year
        ({"release_year": "2000-01-01"}, 1),
        ({"release_year": "2003-01-01"}, 1),
        ({"release_year": "2004-01-01"}, 1),
        # release_year_ge
        ({"release_year_ge": "1899-01-01"}, 5),
        # release_year_le
        ({"release_year_le": "2005-01-01"}, 5),
        # release_year range
        (
            {
                "release_year_ge": "2002-01-01",
                "release_year_le": "2004-01-01",
            },
            3,
        ),
        # Rating
        ({"rating": "0.0"}, 5),
        ({"rating_ge": "1.0"}, 0),
        ({"rating_le": "5"}, 5),
        # No match
        ({"title": "NotExists"}, 0),
        ({"title": "The Hidden Sparrow"}, 0),
        ({"description": "About life exp"}, 0),
        ({"director": "Some guy"}, 0),
        ({"release_year": "1999-01-01"}, 0),
        ({"release_year_ge": "2005-01-01"}, 0),
        ({"release_year_le": "1999-01-01"}, 0),
        # AND CASES FOR GENRES
    ],
)
async def test_get_films(ac, params, target_length):
    res = await ac.get("/films", params=params)
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == target_length


@pytest.mark.parametrize(
    "title, description, director, release_year, duration, cover_url, status_code",
    [
        # Valid data
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "2005-01-01",
            140,
            "https://example.com/valid_url.jpg",
            201,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1999-09-09",
            140,
            None,
            201,
        ),
        # Invalid title
        ("", "Valid Description", "Valid Director", "2006-01-01", 140, None, 422),
        ("T" * 256, "Valid Description", "Valid Director", "2006-01-01", 140, None, 422),
        # Invalid description
        ("Valid Title", "", "Valid Director", "2020-01-01", 140, None, 422),
        ("Valid Title", "D" * 256, "Valid Director", "2020-01-01", 140, None, 422),
        # Invalid director
        ("Valid Title", "Valid Description", "", "2020-01-01", 140, None, 422),
        ("Valid Title", "Valid Description", "D" * 50, "2020-01-01", 140, None, 422),
        # Invalid release year
        ("Valid Title", "Valid Description", "Valid Director", "10-01-01", 90, None, 422),
        ("Valid Title", "Valid Description", "Valid Director", "some-garbage-here", 90, None, 422),
        ("Valid Title", "Valid Description", "Valid Director", 1, 90, None, 422),
        ("Valid Title", "Description", "Director", "2100-01-01", 90, None, 422),
        ("Valid Title", "Description", "Director", "999-01-01", 90, None, 422),
        # Invalid duration
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", -1, None, 422),
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", 513, None, 422),
        # Invalid cover url
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", 140, "not-a-url", 422),
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", 140, 1, 422),
        # All optional fields None (cover_url) - should succeed
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", 140, None, 201),
        # Conflict
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "2020-01-01",
            140,
            "https://example.com/valid_url.jpg",
            409,
        ),
    ],
)
async def test_add_film(
    ac,
    title,
    description,
    director,
    release_year,
    duration,
    cover_url,
    status_code,
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

    if status_code == 201:
        added_film = res.json()["data"]

        assert added_film["title"] == title
        assert added_film["description"] == description
        assert added_film["director"] == director
        assert added_film["release_year"] == release_year
        assert added_film["duration"] == duration
        assert added_film["cover_url"] == cover_url

        films_ids.append(added_film["id"])


@pytest.mark.parametrize(
    "update_data, status_code, film_id",
    [
        # Update title
        ({"title": "Title Updated"}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"title": "Title Updated"}, 200, None),
        # Invalid title
        ({"title": ""}, 422, None),
        ({"title": "T" * 256}, 422, None),
        # Update description
        ({"description": "Description Updated"}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"description": "Description Updated"}, 200, None),
        # Invalid description
        ({"description": ""}, 422, None),
        ({"description": "D" * 256}, 422, None),
        # Update director
        ({"director": "Director Updated"}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"director": "Director Updated"}, 200, None),
        # Invalid director
        ({"director": ""}, 422, None),
        ({"director": "D" * 50}, 422, None),
        # Update release year
        ({"release_year": "2021-01-01"}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"release_year": "2021-01-01"}, 200, None),
        # Invalid release year
        ({"release_year": "10-01-01"}, 422, None),
        ({"release_year": ""}, 422, None),
        ({"release_year": 1}, 422, None),
        ({"release_year": "2100-01-01"}, 422, None),  # future year
        ({"release_year": "999-01-01"}, 422, None),  # too old
        # Update duration
        ({"duration": 120}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"duration": 120}, 200, None),
        # Invalid duration
        ({"duration": -1}, 422, None),
        ({"duration": 513}, 422, None),
        # Update cover_url
        (
            {"cover_url": "https://example.com/updated.jpg"},
            200,
            "2449c8d3-6875-467e-b192-e89dc7a5a7e9",
        ),
        ({"cover_url": "https://example.com/updated.jpg"}, 409, None),  # conflict
        # Invalid cover url
        ({"cover_url": ""}, 422, None),
        ({"cover_url": "invalid-uri"}, 422, None),
        # Update video url
        (
            {"video_url": "https://www.youtube.com/watch?v=vGVeDm4118Q"},
            200,
            "2449c8d3-6875-467e-b192-e89dc7a5a7e9",
        ),
        ({"video_url": "https://www.youtube.com/watch?v=vGVeDm4118Q"}, 409, None),  # conflict
        # Invalid video url
        ({"video_url": ""}, 422, None),
        ({"video_url": "invalid-uri"}, 422, None),
        # Update multiple fields
        (
            {"title": "New Title", "description": "New Description", "director": "New Director"},
            200,
            "2449c8d3-6875-467e-b192-e89dc7a5a7e9",
        ),
        (
            {"title": "New Title", "description": "New Description", "director": "New Director"},
            200,
            None,
        ),
        (
            {
                "duration": 99,
                "release_year": "2022-01-01",
                "cover_url": "https://example.com/test.jpg",
            },
            200,
            "2449c8d3-6875-467e-b192-e89dc7a5a7e9",
        ),
        (
            {
                "duration": 99,
                "release_year": "2022-01-01",
                "cover_url": "https://example.com/test.jpg",
            },
            409,
            None,
        ),  # conflict
    ],
)
async def test_update_film(
    ac,
    update_data,
    status_code,
    film_id,
):
    film_id = film_id or films_ids[0]
    res = await ac.patch(f"/films/{film_id}", json=update_data)
    assert res.status_code == status_code


async def test_delete_film(ac):
    for film_id in films_ids:
        assert (await ac.delete(f"/films/{film_id}")).status_code == 204
        assert (await ac.get(f"/films/{film_id}")).status_code == 404
