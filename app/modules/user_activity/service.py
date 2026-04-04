from app.core.database import prisma
from typing import List, Optional
from datetime import datetime
from app.modules.user_activity.schemas import SavedEpisodeResponse, EpisodeViewResponse

class UserActivityService:
    async def toggle_save_episode(self, user_id: str, episode_id: str) -> dict:
        # Check if already saved
        saved = await prisma.savedepisode.find_unique(
            where={
                "userId_episodeId": {
                    "userId": user_id,
                    "episodeId": episode_id
                }
            }
        )
        
        if saved:
            await prisma.savedepisode.delete(where={"id": saved.id})
            count = await prisma.savedepisode.count(where={"episodeId": episode_id})
            return {"status": "unsaved", "message": "Episode removed from list", "saveCount": count}
        
        await prisma.savedepisode.create(
            data={
                "userId": user_id,
                "episodeId": episode_id
            }
        )
        count = await prisma.savedepisode.count(where={"episodeId": episode_id})
        return {"status": "saved", "message": "Episode saved to list", "saveCount": count}

    async def get_saved_episodes(self, user_id: str) -> List[dict]:
        return await prisma.savedepisode.find_many(
            where={"userId": user_id},
            include={"episode": True},
            order={"createdAt": "desc"}
        )

    async def get_watch_history(self, user_id: str) -> List[dict]:
        return await prisma.episodeview.find_many(
            where={"userId": user_id},
            include={"episode": True},
            order={"createdAt": "desc"}
        )

    async def delete_history_item(self, user_id: str, item_id: str) -> str:
        await prisma.episodeview.delete_many(
            where={
                "id": item_id,
                "userId": user_id
            }
        )
        return "History item deleted"

    async def bulk_delete_history(self, user_id: str, ids: List[str]) -> str:
        await prisma.episodeview.delete_many(
            where={
                "id": {"in": ids},
                "userId": user_id
            }
        )
        return f"{len(ids)} history items deleted"

    async def bulk_remove_saved(self, user_id: str, ids: List[str]) -> str:
        await prisma.savedepisode.delete_many(
            where={
                "id": {"in": ids},
                "userId": user_id
            }
        )
        return f"{len(ids)} episodes removed from list"

    async def clear_all_history(self, user_id: str) -> str:
        await prisma.episodeview.delete_many(where={"userId": user_id})
        return "All watch history cleared"

    async def get_save_count(self, episode_id: str) -> int:
        return await prisma.savedepisode.count(where={"episodeId": episode_id})
