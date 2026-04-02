from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from prisma.enums import EpisodeUnlockMethod, AccessControlStatus

class SeriesBase(BaseModel):
    title: str
    description: str
    categoryId: str
    languageId: str
    keywords: Optional[str] = None
    freeEpisodeLimit: Optional[int] = 0
    episodeUnlockMethod: EpisodeUnlockMethod = EpisodeUnlockMethod.FREE
    coinPerEpisode: Optional[int] = 0
    accessControlStatus: AccessControlStatus = AccessControlStatus.PUBLIC
    isSensitiveContent: bool = False
    tags: Optional[str] = None

class SeriesCreate(SeriesBase):
    pass

class SeriesUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    categoryId: Optional[str] = None
    languageId: Optional[str] = None
    keywords: Optional[str] = None
    thumbnail: Optional[str] = None
    freeEpisodeLimit: Optional[int] = None
    episodeUnlockMethod: Optional[EpisodeUnlockMethod] = None
    coinPerEpisode: Optional[int] = None
    accessControlStatus: Optional[AccessControlStatus] = None
    isSensitiveContent: Optional[bool] = None
    tags: Optional[str] = None

class EpisodeSummaryResponse(BaseModel):
    id: str
    title: str
    description: str
    episodeSerialNumber: int
    thumbnail: Optional[str] = None
    videoFile: Optional[str] = None
    resolution: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    @field_validator("videoFile", mode="before")
    @classmethod
    def force_null_video_file(cls, v):
        return None

    class Config:
        from_attributes = True

class SeriesResponse(SeriesBase):
    id: str
    thumbnail: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    episodes: List[EpisodeSummaryResponse] = []

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaginatedSeriesResponse(BaseModel):
    total: int
    page: int
    size: int
    series: List[SeriesResponse]
