from fastapi import APIRouter

from app.modules.purchases.schemas import PurchaseVerificationRequest, PurchaseVerificationResponse
from app.modules.purchases.service import PurchasesService
from app.core.dependencies import CurrentUserDep

router = APIRouter(prefix="/purchases", tags=["Purchases"])
purchase_service = PurchasesService()

@router.post("/google/verify", response_model=PurchaseVerificationResponse)
async def verify_google_purchase(
    data: PurchaseVerificationRequest,
    current_user: CurrentUserDep
):
    result = await purchase_service.verify_google_purchase(current_user.id, data)
    return result

@router.post("/apple/verify", response_model=PurchaseVerificationResponse)
async def verify_apple_purchase(
    data: PurchaseVerificationRequest,
    current_user: CurrentUserDep
):
    result = await purchase_service.verify_apple_purchase(current_user.id, data)
    return result

@router.post("/google/webhook")
async def google_webhook(data: dict):
    """
    Endpoint for Google Play Real-time Developer Notifications (RTDN).
    This handles subscription renewals, cancellations, and expirations.
    """
    # In production, you would verify the Pub/Sub token/signature here
    result = await purchase_service.handle_google_webhook(data)
    return result
