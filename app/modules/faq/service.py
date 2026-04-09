from app.core.database import prisma
from app.modules.faq.schemas import FaqCreate, FaqUpdate
from typing import List

class FaqService:
    async def get_all_faqs(self):
        """Fetch all FAQs from the database."""
        return await prisma.faq.find_many()

    async def get_faq_by_id(self, faq_id: str):
        """Fetch a specific FAQ by its ID."""
        faq = await prisma.faq.find_unique(where={"id": faq_id})
        if not faq:
            raise ValueError(f"FAQ with ID '{faq_id}' not found.")
        return faq

    async def create_faq(self, data: FaqCreate):
        """Create a new FAQ."""
        faq = await prisma.faq.create(
            data={
                "title": data.title,
                "description": data.description
            }
        )
        return faq

    async def update_faq(self, faq_id: str, data: FaqUpdate):
        """Update an existing FAQ."""
        faq = await prisma.faq.find_unique(where={"id": faq_id})
        if not faq:
            raise ValueError("FAQ not found.")

        update_data = data.model_dump(exclude_unset=True)
        updated_faq = await prisma.faq.update(
            where={"id": faq_id},
            data=update_data
        )
        return updated_faq

    async def delete_faq(self, faq_id: str):
        """Delete an existing FAQ."""
        faq = await prisma.faq.find_unique(where={"id": faq_id})
        if not faq:
            raise ValueError("FAQ not found.")

        await prisma.faq.delete(where={"id": faq_id})
        return {"message": "FAQ deleted successfully."}
