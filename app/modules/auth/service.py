from datetime import datetime, timedelta, timezone
from prisma.enums import OtpPurpose, UserStatus
from app.core.database import prisma
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_reset_password_token,
    decode_token,
    settings,
)
from app.common.exceptions import BadRequestException, NotFoundException, ConflictException, ForbiddenException
from app.modules.auth.schemas import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    ResetTokenResponse,
    OtpVerificationRequest,
    ResetPasswordRequest,
    UserActionRequest,
    UserResponse,
    RefreshTokenRequest,
)
from app.modules.auth.utils import generate_otp, send_verification_email, send_forget_password_email


class AuthService:
    async def signup(self, data: SignupRequest) -> str:
        # Check existing user
        existing_user = await prisma.user.find_first(
            where={
                "OR": [
                    {"email": data.email},
                    {"phoneNumber": data.phoneNumber},
                ]
            }
        )
        if existing_user:
            raise ConflictException("User with this email or phone number already exists")

        # Create user
        hashed_password = hash_password(data.password)
        new_user = await prisma.user.create(
            data={
                "fullName": data.fullName,
                "email": data.email,
                "phoneNumber": data.phoneNumber,
                "password": hashed_password,
            }
        )

        # Generate and save OTP
        await self._create_and_send_otp(new_user.id, new_user.email, new_user.fullName, OtpPurpose.EMAIL_VERIFICATION)

        return "Registration successful. Please check your email for the verification OTP."

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await prisma.user.find_unique(where={"email": data.email})
        if not user or user.isDeleted:
            raise BadRequestException("Invalid email or password")

        if not verify_password(data.password, user.password):
            raise BadRequestException("Invalid email or password")

        from prisma.enums import Role
        if getattr(data, 'isAdminLogin', False) and user.role != Role.ADMIN:
            raise ForbiddenException("Access denied. Only admins can login to the dashboard.")

        if not user.isVerified:
            raise ForbiddenException("Account not verified. Please verify your email first.")

        if user.status != UserStatus.ACTIVE:
            raise ForbiddenException("Account is inactive.")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Save refresh token in database
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await prisma.refreshtoken.create(
            data={
                "token": refresh_token,
                "userId": user.id,
                "expiresAt": expires_at
            }
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            user=UserResponse.model_validate(user)
        )

    async def refresh_token(self, old_refresh_token: str) -> TokenResponse:
        from app.common.exceptions import UnauthorizedException
        
        # Decode and validate token structure and expiry
        try:
            payload = decode_token(old_refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type")
        except Exception:
            raise UnauthorizedException("Invalid or expired refresh token")
            
        user_id: str = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")
            
        # Check database for token
        db_token = await prisma.refreshtoken.find_unique(where={"token": old_refresh_token})
        if not db_token or db_token.isRevoked:
            raise UnauthorizedException("Invalid or revoked refresh token")
            
        # Check user status
        user = await prisma.user.find_unique(where={"id": user_id})
        if not user or user.isDeleted or user.status != UserStatus.ACTIVE:
            raise UnauthorizedException("User account is invalid or inactive")

        # Revoke the old token
        await prisma.refreshtoken.update(
            where={"id": db_token.id},
            data={"isRevoked": True}
        )
        
        # Issue new tokens
        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)
        
        # Save new refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await prisma.refreshtoken.create(
            data={
                "token": new_refresh_token,
                "userId": user.id,
                "expiresAt": expires_at
            }
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            user=UserResponse.model_validate(user)
        )

    async def resend_otp(self, email: str, purpose: OtpPurpose) -> str:
        user = await prisma.user.find_unique(where={"email": email})
        if not user or user.isDeleted:
            raise NotFoundException("User not found")

        if purpose == OtpPurpose.EMAIL_VERIFICATION and user.isVerified:
            raise BadRequestException("User is already verified")

        await self._create_and_send_otp(user.id, user.email, user.fullName, purpose)

        return "OTP sent successfully"

    async def verify_otp(self, data: OtpVerificationRequest) -> str:
        user = await prisma.user.find_unique(where={"email": data.email})
        if not user or user.isDeleted:
            raise NotFoundException("User not found")

        # Find latest valid OTP
        now = datetime.now(timezone.utc)
        otp_record = await prisma.otpcode.find_first(
            where={
                "userId": user.id,
                "code": data.code,
                "purpose": OtpPurpose.EMAIL_VERIFICATION,
                "isUsed": False,
                "expiresAt": {"gt": now}
            },
            order={"createdAt": "desc"}
        )

        if not otp_record:
            raise BadRequestException("Invalid or expired OTP")

        # Mark OTP as used
        await prisma.otpcode.update(
            where={"id": otp_record.id},
            data={"isUsed": True}
        )

        # Update user status
        await prisma.user.update(
            where={"id": user.id},
            data={
                "isVerified": True,
                "status": UserStatus.ACTIVE
            }
        )

        return "Account verified successfully. You can now login."

    async def forget_password(self, email: str) -> str:
        user = await prisma.user.find_unique(where={"email": email})
        if not user or user.isDeleted:
            raise NotFoundException("User not found")

        await self._create_and_send_otp(user.id, user.email, user.fullName, OtpPurpose.FORGET_PASSWORD)

        return "Password reset OTP sent to your email."

    async def verify_forget_password_otp(self, data: OtpVerificationRequest) -> ResetTokenResponse:
        user = await prisma.user.find_unique(where={"email": data.email})
        if not user or user.isDeleted:
            raise NotFoundException("User not found")

        # Find latest valid OTP
        now = datetime.now(timezone.utc)
        otp_record = await prisma.otpcode.find_first(
            where={
                "userId": user.id,
                "code": data.code,
                "purpose": OtpPurpose.FORGET_PASSWORD,
                "isUsed": False,
                "expiresAt": {"gt": now}
            },
            order={"createdAt": "desc"}
        )

        if not otp_record:
            raise BadRequestException("Invalid or expired OTP")

        # Mark OTP as used
        await prisma.otpcode.update(
            where={"id": otp_record.id},
            data={"isUsed": True}
        )

        reset_token = create_reset_password_token(user.id)

        return ResetTokenResponse(
            reset_token=reset_token,
            expires_in=settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES * 60
        )

    async def reset_password(self, user_id: str, new_password: str) -> str:
        hashed_password = hash_password(new_password)
        await prisma.user.update(
            where={"id": user_id},
            data={"password": hashed_password}
        )
        return "Password updated successfully"

    async def user_action(self, data: UserActionRequest) -> str:
        user = await prisma.user.find_unique(where={"id": data.userId})
        if not user:
            raise NotFoundException("User not found")

        update_data = {}
        if data.status == UserStatus.ACTIVE:
            update_data = {"status": UserStatus.ACTIVE, "isDeleted": False}
        elif data.status == UserStatus.INACTIVE:
            update_data = {"status": UserStatus.INACTIVE}

        await prisma.user.update(
            where={"id": data.userId},
            data=update_data
        )

        return f"User status updated to {data.status}"

    async def _create_and_send_otp(self, user_id: str, email: str, name: str, purpose: OtpPurpose):
        # Invalidate existing unused OTPs of the same purpose
        await prisma.otpcode.update_many(
            where={
                "userId": user_id,
                "purpose": purpose,
                "isUsed": False
            },
            data={"isUsed": True}
        )

        otp_code = generate_otp()
        # Ensure UTC timezone
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        await prisma.otpcode.create(
            data={
                "userId": user_id,
                "code": otp_code,
                "purpose": purpose,
                "expiresAt": expires_at
            }
        )

        if purpose == OtpPurpose.EMAIL_VERIFICATION:
            await send_verification_email(email, name, otp_code)
        elif purpose == OtpPurpose.FORGET_PASSWORD:
            await send_forget_password_email(email, name, otp_code)
