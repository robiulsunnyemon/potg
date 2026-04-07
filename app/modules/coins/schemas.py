from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime as DateTime

class CoinPackageCreate(BaseModel):
    id: str = Field(..., description="Unique Package ID, e.g., 100_coins_id")
    packageName: str
    baseCoins: int
    bonusCoins: int = 0
    priceUsd: float

class CoinPackageResponse(BaseModel):
    id: str
    packageName: str
    baseCoins: int
    bonusCoins: int
    priceUsd: float
    createdAt: DateTime
    updatedAt: DateTime

    class Config:
        from_attributes = True

class PaginatedCoinPackageResponse(BaseModel):
    total: int
    packages: List[CoinPackageResponse]
