from app.core.database import prisma
from app.modules.episode.schemas import EpisodeCreate, EpisodeUpdate
from app.common.exceptions import NotFoundException, BadRequestException
from typing import List, Optional

class EpisodeService:
    async def create_episode(self, data: EpisodeCreate, video_url: str) -> dict:
        # Verify series exists
        series = await prisma.series.find_unique(where={"id": data.seriesId})
        if not series:
            raise NotFoundException("Series not found")
            
        return await prisma.episode.create(
            data={
                **data.model_dump(),
                "videoFile": video_url
            }
        )

    async def get_episodes(self, series_id: str) -> List[dict]:
        return await prisma.episode.find_many(
            where={"seriesId": series_id},
            order={"episodeSerialNumber": "asc"}
        )

    async def get_episode(self, episode_id: str, current_user: any) -> dict:
        from prisma.enums import Role, AccessControlStatus, EpisodeUnlockMethod
        from app.common.exceptions import ForbiddenException

        episode = await prisma.episode.find_unique(
            where={"id": episode_id},
            include={"series": True}
        )
        if not episode:
            raise NotFoundException("Episode not found")

        series = episode.series

        # 1. Admin gets all access
        if current_user.role == Role.ADMIN:
            return episode

        # 2. Check if episode is within free limit
        if episode.episodeSerialNumber <= (series.freeEpisodeLimit or 0):
            return episode

        # 3. Check Access Control Status (MEMBER restriction)
        if series.accessControlStatus == AccessControlStatus.MEMBER:
            if not current_user.isPremium:
                raise ForbiddenException("This series is for premium members only.")

        # 4. Check Unlock Method (COIN)
        if series.episodeUnlockMethod == EpisodeUnlockMethod.COIN:
            # Check if already unlocked
            transaction = await prisma.transaction.find_first(
                where={
                    "userId": current_user.id,
                    "episodeId": episode_id
                }
            )
            if not transaction:
                # Deduct coin and Create Transaction record
                coin_needed = series.coinPerEpisode or 0
                if current_user.balance < coin_needed:
                    raise ForbiddenException(f"Insufficient balance. You need {coin_needed} coins to unlock this episode.")

                # Atomic balance deduction and transaction record
                await prisma.user.update(
                    where={"id": current_user.id},
                    data={"balance": {"decrement": coin_needed}}
                )
                await prisma.transaction.create(
                    data={
                        "userId": current_user.id,
                        "episodeId": episode_id,
                        "seriesId": series.id,
                        "amount": coin_needed
                    }
                )
        
        return episode

    async def update_episode(self, episode_id: str, data: EpisodeUpdate) -> dict:
        episode = await prisma.episode.find_unique(where={"id": episode_id})
        if not episode:
            raise NotFoundException("Episode not found")

        update_data = data.model_dump(exclude_unset=True)
        return await prisma.episode.update(
            where={"id": episode_id},
            data=update_data
        )

    async def upload_thumbnail(self, episode_id: str, file_content: bytes, filename: str) -> str:
        from app.core.upload import upload_image_to_cloudinary
        
        episode = await prisma.episode.find_unique(where={"id": episode_id})
        if not episode:
            raise NotFoundException("Episode not found")
            
        image_url = await upload_image_to_cloudinary(file_content, filename)
        
        await prisma.episode.update(
            where={"id": episode_id},
            data={"thumbnail": image_url}
        )
        return image_url

    async def delete_episode(self, episode_id: str) -> str:
        episode = await prisma.episode.find_unique(where={"id": episode_id})
        if not episode:
            raise NotFoundException("Episode not found")
            
        await prisma.episode.delete(where={"id": episode_id})
        return "Episode has been deleted successfully"
