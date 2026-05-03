from fastapi import APIRouter, Depends, Form, File, UploadFile
from typing import List, Optional
from app.common.response import ResponseSchema, create_response
from .schemas import RatingCreate, RatingResponse, SeriesRatingsResponse
from .service import rating_service
from app.core.dependencies import CurrentAdminDep

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
async def get_series_ratings(seriesId: str, isAdmin: bool = False):
    """Fetch all ratings and reviews and stats for a specific series."""
    ratings_data = await rating_service.get_series_ratings(seriesId, show_inactive=isAdmin)
    return create_response(data=ratings_data)

@router.patch("/{ratingId}", response_model=ResponseSchema[RatingResponse])
async def update_rating_status(ratingId: str, isActive: bool, admin: CurrentAdminDep):
    """[Admin Only] Toggle rating active status."""
    rating = await rating_service.update_rating(ratingId, isActive=isActive)
    return create_response(data=rating, message="Rating status updated successfully")

@router.put("/{ratingId}", response_model=ResponseSchema[RatingResponse])
async def update_rating(
    ratingId: str,
    admin: CurrentAdminDep,
    userName: Optional[str] = Form(None),
    stars: Optional[float] = Form(None),
    feedback: Optional[str] = Form(None),
    isActive: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    """[Admin Only] Update a rating's details."""
    rating = await rating_service.update_rating(
        ratingId, userName, stars, feedback, image, isActive
    )
    return create_response(data=rating, message="Rating updated successfully")

@router.delete("/{ratingId}", response_model=ResponseSchema[str])
async def delete_rating(ratingId: str, admin: CurrentAdminDep):
    """[Admin Only] Delete a rating."""
    message = await rating_service.delete_rating(ratingId)
    return create_response(data=message)
