from pydantic import BaseModel
from typing import List
from datetime import datetime as DateTime
from prisma.enums import TargetAudience

class NotificationCreate(BaseModel):
    title: str
    message: str
    targetAudience: TargetAudience

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    targetAudience: TargetAudience
    createdAt: DateTime
    updatedAt: DateTime

    class Config:
        from_attributes = True

class PaginatedNotificationResponse(BaseModel):
    total: int
    page: int
    size: int
    notifications: List[NotificationResponse]
