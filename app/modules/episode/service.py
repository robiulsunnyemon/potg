from app.core.database import prisma
from app.modules.episode.schemas import EpisodeCreate, EpisodeUpdate
from app.common.exceptions import NotFoundException, BadRequestException
from typing import List, Optional

class EpisodeService:
    async def create_episode(self, data: EpisodeCreate, video_content: bytes, filename: str) -> dict:
        from app.core.mux import upload_video_to_mux
        
        # Verify series exists
        series = await prisma.series.find_unique(where={"id": data.seriesId})
        if not series:
            raise NotFoundException("Series not found")
            
        # Upload to Mux
        mux_data = await upload_video_to_mux(video_content)
            
        return await prisma.episode.create(
            data={
                **data.model_dump(),
                "muxAssetId": mux_data["asset_id"],
                "muxPlaybackId": mux_data["playback_id"],
                "duration": mux_data["duration"],
                "isProcessing": False # Set to false since we've got the IDs
            }
        )

    async def get_episodes(self, series_id: str) -> List[dict]:
        return await prisma.episode.find_many(
            where={"seriesId": series_id},
            order={"episodeSerialNumber": "asc"}
        )
    
    async def record_view(self, episode_id: str, user_id: str) -> dict:
        """Records a view for the episode and increments series totalViewers."""
        episode = await prisma.episode.find_unique(
            where={"id": episode_id},
            include={"series": True}
        )
        if not episode:
            raise NotFoundException("Episode not found")
        
        # Create view record
        view = await prisma.episodeview.create(
            data={
                "episodeId": episode_id,
                "userId": user_id
            }
        )
        
        # Increment totalViewers in Series
        await prisma.series.update(
            where={"id": episode.seriesId},
            data={"totalViewers": {"increment": 1}}
        )
        
        return view

    async def get_all_free_episodes(self) -> List[dict]:
        from prisma.enums import EpisodeUnlockMethod, SeriesStatus
        
        series_list = await prisma.series.find_many(
            where={"status": SeriesStatus.PUBLISHED},
            include={"episodes": {"where": {"status": SeriesStatus.PUBLISHED}}}
        )
        
        all_free_episodes = []
        for series in series_list:
            if series.episodeUnlockMethod == EpisodeUnlockMethod.FREE:
                # FREE series: all episodes are free
                all_free_episodes.extend(series.episodes)
            else:
                # COIN or MEMBER series: only up to freeEpisodeLimit
                limit = series.freeEpisodeLimit or 0
                if limit > 0:
                    for episode in series.episodes:
                        if episode.episodeSerialNumber <= limit:
                            all_free_episodes.append(episode)
                    
        return all_free_episodes

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
                async with prisma.tx() as tx:
                    await tx.user.update(
                        where={"id": current_user.id},
                        data={"balance": {"decrement": coin_needed}}
                    )
                    from prisma.enums import TransactionType
                    await tx.transaction.create(
                        data={
                            "userId": current_user.id,
                            "episodeId": episode_id,
                            "seriesId": series.id,
                            "amount": coin_needed,
                            "transactionType": TransactionType.SPEND,
                            "description": f"Unlocked Episode: {episode.title}",
                            "gateway": "INTERNAL",
                            "status": "SUCCESS"
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

    async def delete_episode(self, episode_id: str) -> str:
        episode = await prisma.episode.find_unique(where={"id": episode_id})
        if not episode:
            raise NotFoundException("Episode not found")
            
        await prisma.episode.delete(where={"id": episode_id})
        return "Episode has been deleted successfully"
