from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FaqBase(BaseModel):
    title: str = Field(..., description="The question or title of the FAQ")
    description: str = Field(..., description="The answer or description of the FAQ")

class FaqCreate(FaqBase):
    pass

class FaqUpdate(BaseModel):
    title: Optional[str] = Field(None, description="The updated question or title")
    description: Optional[str] = Field(None, description="The updated answer or description")

class FaqResponse(FaqBase):
    id: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
