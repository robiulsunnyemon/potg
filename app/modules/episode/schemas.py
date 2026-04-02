from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EpisodeBase(BaseModel):
    title: str
    seriesId: str
    description: str
    episodeSerialNumber: int
    resolution: Optional[str] = "1080p"

class EpisodeCreate(EpisodeBase):
    pass

class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    episodeSerialNumber: Optional[int] = None
    thumbnail: Optional[str] = None
    videoFile: Optional[str] = None
    resolution: Optional[str] = None

class EpisodeResponse(EpisodeBase):
    id: str
    thumbnail: Optional[str] = None
    videoFile: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
