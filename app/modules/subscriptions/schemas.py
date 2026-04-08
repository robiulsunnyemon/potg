from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime as DateTime
from prisma.enums import SubscriptionDuration

class SubscriptionPlanCreate(BaseModel):
    id: str = Field(..., description="Unique Package ID")
    packageName: str
    planName: str
    priceUsd: float
    duration: SubscriptionDuration
    benefits: List[str]

class SubscriptionPlanUpdate(BaseModel):
    packageName: Optional[str] = None
    planName: Optional[str] = None
    priceUsd: Optional[float] = None
    duration: Optional[SubscriptionDuration] = None
    benefits: Optional[List[str]] = None

class SubscriptionPlanResponse(BaseModel):
    id: str
    packageName: str
    planName: str
    priceUsd: float
    duration: SubscriptionDuration
    benefits: List[str]
    createdAt: DateTime
    updatedAt: DateTime

    class Config:
        from_attributes = True

class PaginatedSubscriptionPlanResponse(BaseModel):
    total: int
    plans: List[SubscriptionPlanResponse]
