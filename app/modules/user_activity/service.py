from app.core.database import prisma
from typing import List, Optional
from datetime import datetime
from app.modules.user_activity.schemas import SavedSeriesResponse, EpisodeViewResponse

class UserActivityService:
    async def toggle_save_episode(self, user_id: str, episode_id: str) -> dict:
        episode = await prisma.episode.find_unique(where={"id": episode_id})
        if not episode:
            return {"status": "error", "message": "Episode not found"}
            
        series_id = episode.seriesId

        saved = await prisma.savedseries.find_unique(
            where={
                "userId_seriesId": {
                    "userId": user_id,
                    "seriesId": series_id
                }
            }
        )
        
        if saved:
            await prisma.savedseries.delete(where={"id": saved.id})
            count = await prisma.savedseries.count(where={"seriesId": series_id})
            return {"status": "unsaved", "message": "Series removed from list", "saveCount": count}
        
        await prisma.savedseries.create(
            data={
                "userId": user_id,
                "seriesId": series_id
            }
        )
        count = await prisma.savedseries.count(where={"seriesId": series_id})
        return {"status": "saved", "message": "Series saved to list", "saveCount": count}

    async def get_saved_series(self, user_id: str) -> List[dict]:
        saved_series_list = await prisma.savedseries.find_many(
            where={"userId": user_id},
            include={"series": True},
            order={"createdAt": "desc"}
        )
        
        result = []
        for saved in saved_series_list:
            last_view = await prisma.episodeview.find_first(
                where={
                    "userId": user_id,
                    "episode": {"is": {"seriesId": saved.seriesId}}
                },
                include={"episode": True},
                order={"createdAt": "desc"}
            )
            
            last_viewed_episode = None
            if last_view:
                last_viewed_episode = last_view.episode
            else:
                last_viewed_episode = await prisma.episode.find_first(
                    where={"seriesId": saved.seriesId},
                    order={"episodeSerialNumber": "asc"}
                )
            
            saved_data = saved.model_dump() if hasattr(saved, 'model_dump') else saved.dict()
            
            # Fetch and set total episode count
            total_episode = await prisma.episode.count(where={"seriesId": saved.seriesId})
            if "series" in saved_data and saved_data["series"]:
                saved_data["series"]["total_episode"] = total_episode
            
            if last_viewed_episode:
                saved_data["lastViewedEpisode"] = last_viewed_episode.model_dump() if hasattr(last_viewed_episode, 'model_dump') else last_viewed_episode.dict()
            else:
                saved_data["lastViewedEpisode"] = None
                
            result.append(saved_data)
            
        return result

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
        await prisma.savedseries.delete_many(
            where={
                "id": {"in": ids},
                "userId": user_id
            }
        )
        return f"{len(ids)} series removed from list"

    async def clear_all_history(self, user_id: str) -> str:
        await prisma.episodeview.delete_many(where={"userId": user_id})
        return "All watch history cleared"

    async def get_save_count(self, episode_id: str) -> int:
        episode = await prisma.episode.find_unique(where={"id": episode_id})
        if not episode:
            return 0
        return await prisma.savedseries.count(where={"seriesId": episode.seriesId})
