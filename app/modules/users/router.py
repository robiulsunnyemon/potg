from fastapi import APIRouter, Depends, Query, status, File, UploadFile
from app.modules.users.service import UserService
from app.modules.users.schemas import UpdateUserRequest, PaginatedUserResponse, SetPasswordRequest
from app.modules.auth.schemas import UserResponse
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentUserDep, CurrentAdminDep

router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()

@router.get("", response_model=ResponseSchema[PaginatedUserResponse])
async def get_users(
    current_admin: CurrentAdminDep,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """[Admin Only] Fetch all active users with pagination."""
    users_data = await user_service.get_users(page, size)
    return create_response(data=users_data)

@router.get("/me", response_model=ResponseSchema[UserResponse])
async def get_current_user(current_user: CurrentUserDep):
    """[User Only] Fetch the profile of the currently authenticated user."""
    user_data = await user_service.get_user_by_id(current_user.id)
    return create_response(data=user_data)

@router.post("/profile-image", response_model=ResponseSchema[str])
async def upload_image(
    current_user: CurrentUserDep,
    file: UploadFile = File(...)
):
    """[User Only] Upload and update profile image directly to Cloudinary"""
    if not file.content_type.startswith("image/"):
        from app.common.exceptions import BadRequestException
        raise BadRequestException("File provided is not an image.")
        
    file_content = await file.read()
    image_url = await user_service.upload_profile_image(current_user.id, file_content, file.filename)
    return create_response(data=image_url)

@router.patch("/set-password", response_model=ResponseSchema[str])
async def set_password(
    data: SetPasswordRequest,
    current_user: CurrentUserDep
):
    """[User Only] Set a new password without needing the old password."""
    message = await user_service.set_password(current_user.id, data.new_password)
    return create_response(data=message)

@router.get("/{user_id}", response_model=ResponseSchema[UserResponse])
async def get_user(user_id: str, current_user: CurrentUserDep):
    """[Public/Authenticated] Fetch single user profile by id."""
    user_data = await user_service.get_user_by_id(user_id)
    return create_response(data=user_data)

@router.patch("/profile", response_model=ResponseSchema[str])
async def update_user(
    data: UpdateUserRequest,
    current_user: CurrentUserDep
):
    """[User Only] Update own profile (name, phone number)"""
    message = await user_service.update_user(current_user.id, data)
    return create_response(data=message)

@router.delete("/me", response_model=ResponseSchema[str])
async def delete_current_user(current_user: CurrentUserDep):
    """[User Only] Soft delete the currently authenticated user account."""
    message = await user_service.delete_user(current_user.id)
    return create_response(data=message)

@router.delete("/{user_id}", response_model=ResponseSchema[str])
async def delete_user(user_id: str, current_admin: CurrentAdminDep):
    """[Admin Only] Soft delete a user by id."""
    message = await user_service.delete_user(user_id)
    return create_response(data=message)

@router.get("/me/transactions", response_model=ResponseSchema[dict])
async def get_my_transactions(
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """[User Only] Fetch the transaction history of the currently authenticated user."""
    transactions = await user_service.get_user_transactions(current_user.id, page, size)
    return create_response(data=transactions)
@router.get("/me/total-purchased-coins", response_model=ResponseSchema[dict])
async def get_total_purchased_coins(current_user: CurrentUserDep):
    """[User Only] Fetch the total number of coins purchased by the user."""
    result = await user_service.get_total_purchased_coins(current_user.id)
    return create_response(data=result)
