from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class SortBy(StrEnum):
    ID = "id"
    TITLE = "title"
    RELEASE_YEAR = "release_year"
    RATING = "rating"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class ZodiacSign(StrEnum):
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"
