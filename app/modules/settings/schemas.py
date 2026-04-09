from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AppPageBase(BaseModel):
    title: str = Field(..., description="The title of the page (e.g., about-us, privacy-policy)")
    content: str = Field(..., description="The content of the page")

class AppPageCreate(AppPageBase):
    pass

class AppPageUpdate(BaseModel):
    content: str = Field(..., description="The new content of the page")

class AppPageResponse(AppPageBase):
    id: str
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True
