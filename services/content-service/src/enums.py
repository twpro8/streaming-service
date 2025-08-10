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
