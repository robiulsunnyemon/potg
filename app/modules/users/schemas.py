from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from app.modules.auth.schemas import UserResponse

class UpdateUserRequest(BaseModel):
    fullName: Optional[str] = Field(None, min_length=3, max_length=100)
    phoneNumber: Optional[str] = Field(None, min_length=10, max_length=15)

class PaginatedUserResponse(BaseModel):
    total: int
    page: int
    size: int
    users: List[UserResponse]

class SetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        import re
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v
