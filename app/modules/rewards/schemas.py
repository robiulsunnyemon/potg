from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from prisma.enums import RewardDay

class RewardSettingSchema(BaseModel):
    day: RewardDay
    coins: int

class RewardSettingsUpdate(BaseModel):
    settings: List[RewardSettingSchema]

class RewardHistorySchema(BaseModel):
    day: str
    status: str
    coinsRewarded: int
    claimedDate: Optional[datetime] = None

class RewardHistoryResponse(BaseModel):
    history: List[RewardHistorySchema]
    today_status: str
    today_day: str
