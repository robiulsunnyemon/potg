from fastapi import APIRouter, Depends, status
from app.modules.auth.service import AuthService
from app.modules.auth.schemas import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    ResetTokenResponse,
    OtpRequest,
    OtpVerificationRequest,
    ResetPasswordRequest,
    UserActionRequest,
    RefreshTokenRequest,
)
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentAdminDep
from prisma.enums import OtpPurpose
from app.core.security import decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()

@router.post("/", response_model=ResponseSchema[str], status_code=status.HTTP_201_CREATED)
async def signup(data: SignupRequest):
    message = await auth_service.signup(data)
    return create_response(data=message)

@router.post("/login", response_model=ResponseSchema[TokenResponse])
async def login(data: LoginRequest):
    token_response = await auth_service.login(data)
    return create_response(data=token_response)

@router.post("/refresh-token", response_model=ResponseSchema[TokenResponse])
async def refresh_token(data: RefreshTokenRequest):
    token_response = await auth_service.refresh_token(data.refresh_token)
    return create_response(data=token_response)

@router.post("/resend-otp", response_model=ResponseSchema[str])
async def resend_otp(data: OtpRequest):
    message = await auth_service.resend_otp(data.email, OtpPurpose.EMAIL_VERIFICATION)
    return create_response(data=message)

@router.post("/otp-verification", response_model=ResponseSchema[str])
async def verify_otp(data: OtpVerificationRequest):
    message = await auth_service.verify_otp(data)
    return create_response(data=message)

@router.post("/forget-password", response_model=ResponseSchema[str])
async def forget_password(data: OtpRequest):
    message = await auth_service.forget_password(data.email)
    return create_response(data=message)

@router.post("/forget-password-otp-verification", response_model=ResponseSchema[ResetTokenResponse])
async def verify_forget_password_otp(data: OtpVerificationRequest):
    response = await auth_service.verify_forget_password_otp(data)
    return create_response(data=response)

@router.post("/reset-password", response_model=ResponseSchema[str])
async def reset_password(data: ResetPasswordRequest):
    try:
        payload = decode_token(data.token)
    except Exception:
        from app.common.exceptions import UnauthorizedException
        raise UnauthorizedException("Invalid or expired reset token")
        
    if payload.get("type") != "reset":
        from app.common.exceptions import UnauthorizedException
        raise UnauthorizedException("Invalid reset token")
    
    user_id: str = payload.get("sub")
    if not user_id:
         from app.common.exceptions import UnauthorizedException
         raise UnauthorizedException("Invalid reset token")

    message = await auth_service.reset_password(user_id, data.new_password)
    return create_response(data=message)

@router.patch("/user-action", response_model=ResponseSchema[str])
async def user_action(data: UserActionRequest, current_admin: CurrentAdminDep):
    """Admin only endpoint to change user status."""
    message = await auth_service.user_action(data)
    return create_response(data=message)
