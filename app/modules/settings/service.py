from app.core.database import prisma
from app.modules.settings.schemas import AppPageCreate, AppPageUpdate
from typing import List, Optional

class SettingsService:
    async def get_all_pages(self):
        """Fetch all pages from the database."""
        return await prisma.apppage.find_many()

    async def get_page_by_title(self, title: str):
        """Fetch a specific page by its title."""
        page = await prisma.apppage.find_unique(where={"title": title})
        if not page:
            raise ValueError(f"Page with title '{title}' not found.")
        return page

    async def create_page(self, data: AppPageCreate):
        """Create a new page."""
        # Check if a page with the same title already exists
        existing_page = await prisma.apppage.find_unique(where={"title": data.title})
        if existing_page:
            raise ValueError(f"Page with title '{data.title}' already exists.")
            
        page = await prisma.apppage.create(
            data={
                "title": data.title,
                "content": data.content
            }
        )
        return page

    async def update_page(self, page_id: str, data: AppPageUpdate):
        """Update an existing page's content."""
        page = await prisma.apppage.find_unique(where={"id": page_id})
        if not page:
            raise ValueError("Page not found.")
            
        updated_page = await prisma.apppage.update(
            where={"id": page_id},
            data={"content": data.content}
        )
        return updated_page
        
    async def delete_page(self, page_id: str):
        """Delete an existing page."""
        page = await prisma.apppage.find_unique(where={"id": page_id})
        if not page:
            raise ValueError("Page not found.")
            
        await prisma.apppage.delete(where={"id": page_id})
        return {"message": "Page deleted successfully."}
