from pydantic import BaseModel, computed_field
from typing import Optional
from datetime import datetime
from prisma.enums import SeriesStatus

class EpisodeBase(BaseModel):
    title: str
    seriesId: str
    description: str
    episodeSerialNumber: int
    resolution: Optional[str] = "1080p"
    status: SeriesStatus = SeriesStatus.DRAFT

class EpisodeCreate(BaseModel):
    title: str
    seriesId: str
    description: str
    episodeSerialNumber: int
    thumbnail: Optional[str] = None
    resolution: Optional[str] = "1080p"
    status: SeriesStatus = SeriesStatus.DRAFT

class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    episodeSerialNumber: Optional[int] = None
    thumbnail: Optional[str] = None
    videoFile: Optional[str] = None
    resolution: Optional[str] = None
    status: Optional[SeriesStatus] = None

class EpisodeResponse(EpisodeBase):
    id: str
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
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EpisodeViewResponse(BaseModel):
    id: str
    episodeId: str
    userId: str
    createdAt: datetime

    class Config:
        from_attributes = True
