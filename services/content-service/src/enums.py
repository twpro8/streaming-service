from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class SortBy(StrEnum):
    id = "id"
    title = "title"
    year = "year"
    rating = "rating"
    created_at = "created_at"
    updated_at = "updated_at"


class SortOrder(StrEnum):
    asc = "asc"
    desc = "desc"


class ZodiacSign(StrEnum):
    aries = "Aries"
    taurus = "Taurus"
    gemini = "Gemini"
    cancer = "Cancer"
    leo = "Leo"
    virgo = "Virgo"
    libra = "Libra"
    scorpio = "Scorpio"
    sagittarius = "Sagittarius"
    capricorn = "Capricorn"
    aquarius = "Aquarius"
    pisces = "Pisces"


class ContentType(str, Enum):
    movie = "movie"
    show = "show"

    def __str__(self):
        return self.value
