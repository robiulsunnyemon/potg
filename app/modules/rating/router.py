from fastapi import APIRouter, Depends, Form, File, UploadFile
from typing import List, Optional
from app.common.response import ResponseSchema, create_response
from .schemas import RatingCreate, RatingResponse, SeriesRatingsResponse
from .service import rating_service

router = APIRouter(prefix="/ratings", tags=["Ratings"])

@router.post("", response_model=ResponseSchema[RatingResponse])
async def create_rating(
    userName: str = Form(...),
    stars: float = Form(...),
    feedback: str = Form(...),
    seriesId: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    """Admin endpoint to create a manual rating/review for a series with image upload."""
    rating = await rating_service.create_rating(userName, stars, feedback, seriesId, image)
    return create_response(data=rating)

@router.get("/series/{seriesId}", response_model=ResponseSchema[SeriesRatingsResponse])
async def get_series_ratings(seriesId: str):
    """Fetch all ratings and reviews and stats for a specific series."""
    ratings_data = await rating_service.get_series_ratings(seriesId)
    return create_response(data=ratings_data)
