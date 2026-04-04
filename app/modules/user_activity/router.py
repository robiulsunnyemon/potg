from fastapi import APIRouter, Depends, status
from app.modules.user_activity.service import UserActivityService
from app.modules.user_activity.schemas import SavedEpisodeResponse, EpisodeViewResponse, BulkDeleteRequest
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentUserDep
from typing import List

router = APIRouter(prefix="/user-activity", tags=["User Activity"])
user_activity_service = UserActivityService()

@router.get("/saved", response_model=ResponseSchema[List[SavedEpisodeResponse]])
async def get_saved(user: CurrentUserDep):
    """Fetch all saved episodes for the current user."""
    saved = await user_activity_service.get_saved_episodes(user.id)
    return create_response(data=saved)

@router.post("/saved/{episodeId}", response_model=ResponseSchema[dict])
async def toggle_save(episodeId: str, user: CurrentUserDep):
    """Toggle save/unsave for an episode."""
    result = await user_activity_service.toggle_save_episode(user.id, episodeId)
    return create_response(data=result)

@router.get("/saved/count/{episodeId}", response_model=ResponseSchema[int])
async def get_save_count(episodeId: str):
    """Fetch the total save/follow count for a specific episode."""
    count = await user_activity_service.get_save_count(episodeId)
    return create_response(data=count)

@router.delete("/saved", response_model=ResponseSchema[str])
async def bulk_remove_saved(data: BulkDeleteRequest, user: CurrentUserDep):
    """[Bulk] Remove multiple episodes from My List."""
    message = await user_activity_service.bulk_remove_saved(user.id, data.ids)
    return create_response(data=message)

@router.get("/history", response_model=ResponseSchema[List[EpisodeViewResponse]])
async def get_history(user: CurrentUserDep):
    """Fetch watch history for the current user."""
    history = await user_activity_service.get_watch_history(user.id)
    return create_response(data=history)

@router.delete("/history/{id}", response_model=ResponseSchema[str])
async def delete_history_item(id: str, user: CurrentUserDep):
    """Delete a single watch history item."""
    message = await user_activity_service.delete_history_item(user.id, id)
    return create_response(data=message)

@router.delete("/history", response_model=ResponseSchema[str])
async def clear_history(user: CurrentUserDep, data: BulkDeleteRequest = None):
    """Delete specific items or clear all watch history."""
    if data and data.ids:
        message = await user_activity_service.bulk_delete_history(user.id, data.ids)
    else:
        message = await user_activity_service.clear_all_history(user.id)
    return create_response(data=message)
