from app.core.database import prisma
from app.modules.language.schemas import LanguageCreate, LanguageUpdate
from app.common.exceptions import BadRequestException, NotFoundException

class LanguageService:
    async def create_language(self, data: LanguageCreate):
        existing = await prisma.language.find_unique(where={"name": data.name})
        if existing:
            raise BadRequestException(f"Language with name '{data.name}' already exists.")
        return await prisma.language.create(data=data.model_dump())

    async def get_languages(self):
        return await prisma.language.find_many()

    async def get_language(self, language_id: str):
        language = await prisma.language.find_unique(where={"id": language_id})
        if not language:
            raise NotFoundException("Language not found")
        return language

    async def update_language(self, language_id: str, data: LanguageUpdate):
        await self.get_language(language_id)
        if data.name:
            existing = await prisma.language.find_unique(where={"name": data.name})
            if existing and existing.id != language_id:
                raise BadRequestException(f"Language with name '{data.name}' already exists.")
        return await prisma.language.update(
            where={"id": language_id},
            data=data.model_dump(exclude_unset=True)
        )

    async def delete_language(self, language_id: str):
        await self.get_language(language_id)
        await prisma.language.delete(where={"id": language_id})
        return "Language deleted successfully"
