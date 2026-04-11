from pydantic import BaseModel
from typing import Optional

class PurchaseVerificationRequest(BaseModel):
    productId: str
    purchaseToken: str
    packageName: Optional[str] = None

class PurchaseVerificationResponse(BaseModel):
    success: bool
    message: str
    newBalance: Optional[int] = None
    orderId: Optional[str] = None
