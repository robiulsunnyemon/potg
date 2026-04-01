from app.core.database import prisma
from app.modules.users.schemas import UpdateUserRequest, PaginatedUserResponse
from app.common.exceptions import NotFoundException, ForbiddenException, ConflictException

class UserService:
    async def get_users(self, page: int = 1, size: int = 10) -> PaginatedUserResponse:
        skip = (page - 1) * size
        total_users = await prisma.user.count(where={"isDeleted": False})
        users = await prisma.user.find_many(
            where={"isDeleted": False},
            skip=skip,
            take=size,
            order={"createdAt": "desc"}
        )
        return PaginatedUserResponse(
            total=total_users,
            page=page,
            size=size,
            users=users
        )

    async def get_user_by_id(self, user_id: str) -> dict:
        user = await prisma.user.find_first(
            where={"id": user_id, "isDeleted": False}
        )
        if not user:
            raise NotFoundException("User not found.")
        return user.model_dump()

    async def update_user(self, user_id: str, data: UpdateUserRequest) -> str:
        user = await prisma.user.find_first(
            where={"id": user_id, "isDeleted": False}
        )
        if not user:
            raise NotFoundException("User not found.")

        # Check if phone number is already taken by another user
        if data.phoneNumber:
            phone_exists = await prisma.user.find_first(
                where={"phoneNumber": data.phoneNumber, "id": {"not": user_id}}
            )
            if phone_exists:
                raise ConflictException("Phone number is already currently in use.")

        update_data = {k: v for k, v in data.model_dump(exclude_none=True).items()}
        if not update_data:
            return "No fields to update."

        await prisma.user.update(
            where={"id": user_id},
            data=update_data
        )
        
        return "User profile updated successfully."

    async def delete_user(self, user_id: str) -> str:
        from prisma.enums import UserStatus
        # Soft delete logic
        user = await prisma.user.find_first(
            where={"id": user_id, "isDeleted": False}
        )
        if not user:
            raise NotFoundException("User not found or previously deleted.")

        await prisma.user.update(
            where={"id": user_id},
            data={"isDeleted": True, "status": UserStatus.INACTIVE}
        )
        return "User has been safely deleted."

    async def upload_profile_image(self, user_id: str, file_content: bytes, filename: str) -> str:
        from app.core.upload import upload_image_to_cloudinary
        
        user = await prisma.user.find_first(
            where={"id": user_id, "isDeleted": False}
        )
        if not user:
            raise NotFoundException("User not found.")

        # Upload to Cloudinary
        image_url = await upload_image_to_cloudinary(file_content, filename)
        
        # Save to DB
        await prisma.user.update(
            where={"id": user_id},
            data={"profileImage": image_url}
        )
        
        return image_url

    async def set_password(self, user_id: str, new_password: str) -> str:
        from app.core.security import hash_password
        user = await prisma.user.find_first(
            where={"id": user_id, "isDeleted": False}
        )
        if not user:
            raise NotFoundException("User not found.")

        hashed_password = hash_password(new_password)
        await prisma.user.update(
            where={"id": user_id},
            data={"password": hashed_password}
        )
        return "Password successfully updated."
