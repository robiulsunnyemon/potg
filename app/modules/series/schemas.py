from pydantic import BaseModel, field_validator, computed_field
from typing import Optional, List
from datetime import datetime
from prisma.enums import EpisodeUnlockMethod, AccessControlStatus, SeriesStatus

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
    status: SeriesStatus = SeriesStatus.DRAFT
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
    status: Optional[SeriesStatus] = None
    isSensitiveContent: Optional[bool] = None
    tags: Optional[str] = None

class EpisodeSummaryResponse(BaseModel):
    id: str
    title: str
    description: str
    episodeSerialNumber: int
    thumbnail: Optional[str] = None
    muxAssetId: Optional[str] = None
    muxPlaybackId: Optional[str] = None
    duration: Optional[float] = None
    isProcessing: bool = True
    status: SeriesStatus = SeriesStatus.DRAFT
    createdAt: datetime
    updatedAt: datetime

    @computed_field
    @property
    def hlsUrl(self) -> Optional[str]:
        if self.muxPlaybackId:
            return f"https://stream.mux.com/{self.muxPlaybackId}.m3u8"
        return None

    class Config:
        from_attributes = True

class SeriesResponse(SeriesBase):
    id: str
    thumbnail: Optional[str] = None
    totalViewers: int = 0
    createdAt: datetime
    updatedAt: datetime
    episodes: Optional[List[EpisodeSummaryResponse]] = []

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
