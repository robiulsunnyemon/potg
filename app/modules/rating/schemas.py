from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class RatingBase(BaseModel):
    userName: str
    userImage: Optional[str] = None
    stars: float = Field(..., ge=0, le=5)
    feedback: str
    seriesId: str

class RatingCreate(RatingBase):
    pass

class RatingResponse(RatingBase):
    id: str
    isActive: bool
    createdAt: datetime
    model_config = ConfigDict(from_attributes=True)

class SeriesRatingsResponse(BaseModel):
    averageRating: float
    ratingCount: int
    ratings: List[RatingResponse]
