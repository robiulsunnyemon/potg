from app.core.database import prisma
from .schemas import RatingCreate
from typing import List, Dict, Optional

from fastapi import UploadFile
from app.core.upload import upload_image_to_cloudinary

class RatingService:
    async def create_rating(self, userName: str, stars: float, feedback: str, seriesId: str, image: Optional[UploadFile] = None):
        user_image_url = None
        if image:
            content = await image.read()
            user_image_url = await upload_image_to_cloudinary(content, image.filename)

        return await prisma.rating.create(
            data={
                "userName": userName,
                "userImage": user_image_url,
                "stars": stars,
                "feedback": feedback,
                "seriesId": seriesId
            }
        )

    async def get_series_ratings(self, series_id: str):
        ratings = await prisma.rating.find_many(
            where={"seriesId": series_id, "isActive": True},
            order={"createdAt": "desc"}
        )
        
        stats = await self.get_series_rating_stats(series_id)
        
        return {
            "averageRating": stats["averageRating"],
            "ratingCount": stats["ratingCount"],
            "ratings": ratings
        }

    @staticmethod
    async def get_series_rating_stats(series_id: str) -> Dict[str, any]:
        ratings = await prisma.rating.find_many(where={"seriesId": series_id, "isActive": True})
        if not ratings:
            return {"averageRating": 0.0, "ratingCount": 0}
        
        total_stars = sum(r.stars for r in ratings)
        count = len(ratings)
        return {
            "averageRating": round(total_stars / count, 1),
            "ratingCount": count
        }

rating_service = RatingService()
