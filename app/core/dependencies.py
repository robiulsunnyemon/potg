from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.database import prisma
from app.core.security import decode_token

bearer_scheme = HTTPBearer()

CredentialsDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]


async def get_current_user(credentials: CredentialsDep):
    """
    Decode Bearer token, verify it is an access token,
    and return the active (non-deleted) user from the DB.
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise exc
        user_id: str = payload.get("sub")
        if not user_id:
            raise exc
    except JWTError:
        raise exc

    user = await prisma.user.find_first(
        where={"id": user_id, "isDeleted": False}
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    from prisma.enums import UserStatus
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please verify your email.",
        )
    return user


async def get_current_admin(current_user=Depends(get_current_user)):
    """Ensure the current user has ADMIN role."""
    from prisma.enums import Role
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_user


CurrentUserDep = Annotated[object, Depends(get_current_user)]
CurrentAdminDep = Annotated[object, Depends(get_current_admin)]
