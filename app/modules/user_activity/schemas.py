from pydantic import BaseModel, computed_field
from typing import Optional, List
from datetime import datetime

class EpisodeSummary(BaseModel):
    id: str
    title: str
    description: str
    episodeSerialNumber: int
    thumbnail: Optional[str] = None
    muxPlaybackId: Optional[str] = None
    isProcessing: bool = False
    saveCount: int = 0
    createdAt: datetime

    @computed_field
    @property
    def hlsUrl(self) -> Optional[str]:
        if self.muxPlaybackId:
            return f"https://stream.mux.com/{self.muxPlaybackId}.m3u8"
        return None

class SeriesSummary(BaseModel):
    id: str
    title: str
    description: str
    thumbnail: Optional[str] = None
    createdAt: datetime
    
class SavedSeriesResponse(BaseModel):
    id: str
    seriesId: str
    createdAt: datetime
    series: SeriesSummary
    lastViewedEpisode: Optional[EpisodeSummary] = None

    class Config:
        from_attributes = True

class EpisodeViewResponse(BaseModel):
    id: str
    episodeId: str
    createdAt: datetime
    episode: EpisodeSummary

    class Config:
        from_attributes = True

class BulkDeleteRequest(BaseModel):
    ids: List[str]
