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

    async def get_episode(self, episode_id: str) -> dict:
        episode = await prisma.episode.find_unique(where={"id": episode_id})
        if not episode:
            raise NotFoundException("Episode not found")
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
