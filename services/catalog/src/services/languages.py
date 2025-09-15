from src.exceptions import LanguageNotFoundException, LanguageAlreadyExistsException
from src.schemas.languages import LanguageAddRequestDTO, LanguageAddDTO
from src.services.base import BaseService


class LanguageService(BaseService):
    async def get_languages(self, page: int, per_page: int):
        return await self.db.languages.get_filtered(page=page, per_page=per_page)

    async def get_language(self, lang_id: int):
        lang = await self.db.languages.get_one_or_none(id=lang_id)
        if lang is None:
            raise LanguageNotFoundException
        return lang

    async def add_language(self, lang_data: LanguageAddRequestDTO):
        _lang_data = LanguageAddDTO(code=lang_data.code, name=lang_data.name)
        try:
            lang_id = await self.db.languages.add_language(_lang_data)
        except LanguageAlreadyExistsException:
            raise
        await self.db.commit()
        return lang_id

    async def delete_language(self, lang_id: int):
        await self.db.languages.delete(id=lang_id)
        await self.db.commit()
