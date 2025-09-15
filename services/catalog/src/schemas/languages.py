import pycountry
from pydantic_extra_types.language_code import LanguageAlpha2, LanguageName

from src.schemas.base import BaseSchema


class LanguageAddRequestDTO(BaseSchema):
    code: LanguageAlpha2

    @property
    def name(self) -> LanguageName:
        return pycountry.languages.get(alpha_2=self.code).name


class LanguageAddDTO(BaseSchema):
    code: LanguageAlpha2
    name: LanguageName


class LanguageDTO(LanguageAddDTO):
    id: int
