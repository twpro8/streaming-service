from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class SortBy(StrEnum):
    id = "id"
    title = "title"
    release_year = "release_year"
    rating = "rating"


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
