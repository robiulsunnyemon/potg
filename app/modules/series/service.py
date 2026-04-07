from app.core.database import prisma
from app.modules.series.schemas import SeriesCreate, SeriesUpdate
from app.common.exceptions import NotFoundException, BadRequestException
from typing import List, Optional

class SeriesService:
    async def create_series(self, data: SeriesCreate) -> dict:
        # Verify category exists
        category = await prisma.category.find_unique(where={"id": data.categoryId})
        if not category:
            raise NotFoundException("Category not found")
        
        # Verify language exists
        language = await prisma.language.find_unique(where={"id": data.languageId})
        if not language:
            raise NotFoundException("Language not found")
            
        return await prisma.series.create(data=data.model_dump())

    async def get_series_list(self, page: int = 1, size: int = 10, category_id: Optional[str] = None) -> dict:
        from app.modules.rating.service import rating_service
        skip = (page - 1) * size
        where = {}
        if category_id:
            where["categoryId"] = category_id
            
        # Default to PUBLISHED for non-dashboard use (this can be improved by checking roles)
        # For now, let the dashboard pass an explicit filter if it wants DRAFT
        # or we can add a 'show_drafts' parameter.
            
        total_series = await prisma.series.count(where=where)
        series_list = await prisma.series.find_many(
            where=where,
            skip=skip,
            take=size,
            order={"createdAt": "desc"},
            include={"episodes": True}
        )
        
        # Inject rating stats for each series
        enhanced_series_list = []
        for s in series_list:
            stats = await rating_service.get_series_rating_stats(s.id)
            # Convert to dict and add extra fields
            s_dict = s.model_dump()
            s_dict["averageRating"] = stats["averageRating"]
            s_dict["ratingCount"] = stats["ratingCount"]
            enhanced_series_list.append(s_dict)

        return {
            "total": total_series,
            "page": page,
            "size": size,
            "series": enhanced_series_list
        }

    async def get_series(self, series_id: str) -> dict:
        from app.modules.rating.service import rating_service
        series = await prisma.series.find_unique(
            where={"id": series_id},
            include={"category": True, "language": True, "episodes": True}
        )
        if not series:
            raise NotFoundException("Series not found")
        
        stats = await rating_service.get_series_rating_stats(series_id)
        series_dict = series.model_dump()
        series_dict["averageRating"] = stats["averageRating"]
        series_dict["ratingCount"] = stats["ratingCount"]
        
        return series_dict

    async def update_series(self, series_id: str, data: SeriesUpdate) -> dict:
        series = await prisma.series.find_unique(where={"id": series_id})
        if not series:
            raise NotFoundException("Series not found")

        update_data = data.model_dump(exclude_unset=True)
        
        if "categoryId" in update_data:
            category = await prisma.category.find_unique(where={"id": update_data["categoryId"]})
            if not category:
                raise NotFoundException("Category not found")
                
        if "languageId" in update_data:
            language = await prisma.language.find_unique(where={"id": update_data["languageId"]})
            if not language:
                raise NotFoundException("Language not found")

        return await prisma.series.update(
            where={"id": series_id},
            data=update_data
        )

    async def upload_thumbnail(self, series_id: str, file_content: bytes, filename: str) -> str:
        from app.core.upload import upload_image_to_cloudinary
        
        series = await prisma.series.find_unique(where={"id": series_id})
        if not series:
            raise NotFoundException("Series not found")
            
        image_url = await upload_image_to_cloudinary(file_content, filename)
        
        await prisma.series.update(
            where={"id": series_id},
            data={"thumbnail": image_url}
        )
        return image_url

    async def delete_series(self, series_id: str) -> str:
        series = await prisma.series.find_unique(where={"id": series_id})
        if not series:
            raise NotFoundException("Series not found")
            
        await prisma.series.delete(where={"id": series_id})
        return "Series has been deleted successfully"
