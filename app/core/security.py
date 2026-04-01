from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt
import bcrypt

from app.core.config import settings

# ──────────────────────────────────────────
# Password Utilities
# ──────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Hash a plain password using bcrypt."""
    pwd_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    pwd_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


# ──────────────────────────────────────────
# JWT Utilities
# ──────────────────────────────────────────

def _create_token(
    subject: str,
    token_type: Literal["access", "refresh", "reset"],
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Internal helper to create a JWT token."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: str) -> str:
    """Create a JWT access token (7 days)."""
    return _create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
    )


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token (7 days)."""
    return _create_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_reset_password_token(user_id: str) -> str:
    """Create a short-lived password reset token (15 minutes)."""
    return _create_token(
        subject=user_id,
        token_type="reset",
        expires_delta=timedelta(minutes=settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    Raises JWTError if token is invalid or expired.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
