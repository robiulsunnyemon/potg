from app.core.database import prisma
from app.modules.notification.schemas import NotificationCreate, PaginatedNotificationResponse
from prisma.enums import TargetAudience, UserStatus
from datetime import datetime, timezone

class NotificationService:
    async def create_notification(self, data: NotificationCreate):
        notification = await prisma.notification.create(
            data={
                "title": data.title,
                "message": data.message,
                "targetAudience": data.targetAudience,
            }
        )
        return notification

    async def get_user_notifications(self, user_id: str, page: int = 1, size: int = 20) -> PaginatedNotificationResponse:
        user = await prisma.user.find_first(where={"id": user_id})
        
        audiences = [TargetAudience.ALL]
        if user:
            if user.isPremium:
                audiences.append(TargetAudience.VIP)
            else:
                audiences.append(TargetAudience.FREE)
            
            if user.status == UserStatus.INACTIVE:
                audiences.append(TargetAudience.INACTIVE)
                
            # user.createdAt is offset-aware from prisma
            now_utc = datetime.now(timezone.utc)
            if hasattr(user.createdAt, "tzinfo") and user.createdAt.tzinfo is not None:
                days_since_created = (now_utc - user.createdAt).days
            else:
                days_since_created = (datetime.now() - user.createdAt).days

            if days_since_created <= 7:
                audiences.append(TargetAudience.NEW)

        skip = (page - 1) * size
        total = await prisma.notification.count(
            where={
                "targetAudience": {"in": audiences}
            }
        )
        
        notifications = await prisma.notification.find_many(
            where={
                "targetAudience": {"in": audiences}
            },
            skip=skip,
            take=size,
            order={"createdAt": "desc"}
        )

        return PaginatedNotificationResponse(
            total=total,
            page=page,
            size=size,
            notifications=notifications
        )
