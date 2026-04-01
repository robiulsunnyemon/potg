import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr, field_validator
from prisma.enums import Role, UserStatus

class SignupRequest(BaseModel):
    fullName: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    phoneNumber: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("phoneNumber")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v.isdigit() and not (v.startswith('+') and v[1:].isdigit()):
            raise ValueError("Phone number must contain only digits (and optional leading '+')")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class ResetTokenResponse(BaseModel):
    reset_token: str
    token_type: str = "bearer"
    expires_in: int

class OtpRequest(BaseModel):
    email: EmailStr

class OtpVerificationRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserActionRequest(BaseModel):
    userId: str
    status: UserStatus

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    fullName: str
    email: EmailStr
    phoneNumber: str
    isVerified: bool
    status: UserStatus
    balance: int
    profileImage: Optional[str] = None
    isDeleted: bool
    role: Role
    isPremium: bool

    class Config:
        from_attributes = True
