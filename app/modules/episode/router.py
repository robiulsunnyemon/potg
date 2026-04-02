from fastapi import APIRouter, Depends, status, File, UploadFile, Form
from app.modules.episode.service import EpisodeService
from app.modules.episode.schemas import EpisodeCreate, EpisodeUpdate, EpisodeResponse
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentAdminDep, CurrentUserDep
from typing import List, Optional
import json

router = APIRouter(prefix="/episodes", tags=["Episodes"])
episode_service = EpisodeService()

@router.post("", response_model=ResponseSchema[EpisodeResponse], status_code=status.HTTP_201_CREATED)
async def create_episode(
    admin: CurrentAdminDep,
    data: str = Form(...),
    video: UploadFile = File(...)
):
    """[Admin Only] Create a new episode with video upload."""
    from app.core.upload import upload_video_to_cloudinary
    
    # Parse json data from form field
    try:
        episode_data_dict = json.loads(data)
        episode_create = EpisodeCreate(**episode_data_dict)
    except Exception as e:
        from app.common.exceptions import BadRequestException
        raise BadRequestException(f"Invalid episode data format: {e}")
        
    if not video.content_type.startswith("video/"):
        from app.common.exceptions import BadRequestException
        raise BadRequestException("File provided is not a video.")
        
    video_content = await video.read()
    video_url = await upload_video_to_cloudinary(video_content, video.filename)
    
    episode = await episode_service.create_episode(episode_create, video_url)
    return create_response(data=episode, message="Episode created successfully with video upload")

@router.get("/series/{series_id}", response_model=ResponseSchema[List[EpisodeResponse]])
async def list_episodes(series_id: str):
    """Fetch all episodes for a specific series."""
    episodes = await episode_service.get_episodes(series_id)
    return create_response(data=episodes)

@router.get("/{episode_id}", response_model=ResponseSchema[EpisodeResponse])
async def get_episode(episode_id: str, current_user: CurrentUserDep):
    """Fetch details of a single episode with access control."""
    episode = await episode_service.get_episode(episode_id, current_user)
    return create_response(data=episode)

@router.patch("/{episode_id}", response_model=ResponseSchema[EpisodeResponse])
async def update_episode(episode_id: str, data: EpisodeUpdate, admin: CurrentAdminDep):
    """[Admin Only] Update an existing episode info."""
    episode = await episode_service.update_episode(episode_id, data)
    return create_response(data=episode, message="Episode updated successfully")

@router.post("/{episode_id}/thumbnail", response_model=ResponseSchema[str])
async def upload_thumbnail(
    episode_id: str,
    admin: CurrentAdminDep,
    file: UploadFile = File(...)
):
    """[Admin Only] Upload and update episode thumbnail."""
    if not file.content_type.startswith("image/"):
        from app.common.exceptions import BadRequestException
        raise BadRequestException("File provided is not an image.")
    
    file_content = await file.read()
    image_url = await episode_service.upload_thumbnail(episode_id, file_content, file.filename)
    return create_response(data=image_url, message="Episode thumbnail uploaded successfully")

@router.delete("/{episode_id}", response_model=ResponseSchema[str])
async def delete_episode(episode_id: str, admin: CurrentAdminDep):
    """[Admin Only] Delete an episode by id."""
    message = await episode_service.delete_episode(episode_id)
    return create_response(data=message)
