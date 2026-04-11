from pydantic import BaseModel
from typing import Optional, Dict, Any

class GoogleNotification(BaseModel):
    version: str
    packageName: str
    eventTimeMillis: str
    # One of subscriptionNotification or oneTimeProductNotification will be present
    subscriptionNotification: Optional[Dict[str, Any]] = None
    oneTimeProductNotification: Optional[Dict[str, Any]] = None
    testNotification: Optional[Dict[str, Any]] = None

class RTDNRequest(BaseModel):
    message: Dict[str, Any]
    subscription: str
