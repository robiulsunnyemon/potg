from fastapi import APIRouter, Query, status
from app.modules.notification.service import NotificationService
from app.modules.notification.schemas import NotificationCreate, PaginatedNotificationResponse, NotificationResponse
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentUserDep, CurrentAdminDep

router = APIRouter(prefix="/notifications", tags=["Notifications"])
notification_service = NotificationService()

@router.post("", response_model=ResponseSchema[NotificationResponse], status_code=status.HTTP_201_CREATED)
async def create_notification(
    data: NotificationCreate,
    current_admin: CurrentAdminDep
):
    """[Admin Only] Create a push notification."""
    notification = await notification_service.create_notification(data)
    return create_response(data=notification, message="Notification sent successfully.")

@router.get("", response_model=ResponseSchema[PaginatedNotificationResponse])
async def get_my_notifications(
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """[User Only] Get notifications tailored to the current user."""
    notifications = await notification_service.get_user_notifications(current_user.id, page, size)
    return create_response(data=notifications)
