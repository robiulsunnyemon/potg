from app.core.database import prisma
from app.modules.category.schemas import CategoryCreate, CategoryUpdate
from app.common.exceptions import BadRequestException, NotFoundException

class CategoryService:
    async def create_category(self, data: CategoryCreate):
        existing = await prisma.category.find_unique(where={"name": data.name})
        if existing:
            raise BadRequestException(f"Category with name '{data.name}' already exists.")
        return await prisma.category.create(data=data.model_dump())

    async def get_categories(self):
        return await prisma.category.find_many()

    async def get_category(self, category_id: str):
        category = await prisma.category.find_unique(where={"id": category_id})
        if not category:
            raise NotFoundException("Category not found")
        return category

    async def update_category(self, category_id: str, data: CategoryUpdate):
        await self.get_category(category_id)
        if data.name:
            existing = await prisma.category.find_unique(where={"name": data.name})
            if existing and existing.id != category_id:
                raise BadRequestException(f"Category with name '{data.name}' already exists.")
        return await prisma.category.update(
            where={"id": category_id},
            data=data.model_dump(exclude_unset=True)
        )

    async def delete_category(self, category_id: str):
        await self.get_category(category_id)
        await prisma.category.delete(where={"id": category_id})
        return "Category deleted successfully"
