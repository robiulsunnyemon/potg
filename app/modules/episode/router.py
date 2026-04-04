from fastapi import APIRouter, Depends, status, File, UploadFile, Form
from app.modules.episode.service import EpisodeService
from app.modules.episode.schemas import EpisodeCreate, EpisodeUpdate, EpisodeResponse, EpisodeViewResponse
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentAdminDep, CurrentUserDep
from typing import List, Optional
import json

router = APIRouter(prefix="/episodes", tags=["Episodes"])
episode_service = EpisodeService()

@router.post("", response_model=ResponseSchema[EpisodeResponse], status_code=status.HTTP_201_CREATED)
async def create_episode(
    admin: CurrentAdminDep,
    title: str = Form(...),
    seriesId: str = Form(...),
    description: str = Form(...),
    episodeSerialNumber: int = Form(...),
    resolution: Optional[str] = Form("1080p"),
    thumbnail: UploadFile = File(...),
    video: UploadFile = File(...)
):
    """[Admin Only] Create a new episode with both thumbnail and video uploads."""
    from app.core.upload import upload_image_to_cloudinary
    from app.common.exceptions import BadRequestException
    
    # Validation
    if not video.content_type.startswith("video/"):
        raise BadRequestException("File provided for 'video' is not a video.")
    if not thumbnail.content_type.startswith("image/"):
        raise BadRequestException("File provided for 'thumbnail' is not an image.")
        
    # Upload Thumbnail to Cloudinary
    thumbnail_content = await thumbnail.read()
    thumbnail_url = await upload_image_to_cloudinary(thumbnail_content, thumbnail.filename)
        
    episode_create = EpisodeCreate(
        title=title,
        seriesId=seriesId,
        description=description,
        episodeSerialNumber=episodeSerialNumber,
        thumbnail=thumbnail_url,
        resolution=resolution
    )
    
    # Upload Video to Cloudflare Stream (Service handles this)
    video_content = await video.read()
    episode = await episode_service.create_episode(episode_create, video_content, video.filename)
    return create_response(data=episode, message="Episode created successfully with video and thumbnail")

@router.post("/{episode_id}/view", response_model=ResponseSchema[EpisodeViewResponse])
async def record_view(episode_id: str, user: CurrentUserDep):
    """Record a view for the episode and increment series total views."""
    view = await episode_service.record_view(episode_id, user.id)
    return create_response(data=view, message="View recorded successfully")

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

@router.delete("/{episode_id}", response_model=ResponseSchema[str])
async def delete_episode(episode_id: str, admin: CurrentAdminDep):
    """[Admin Only] Delete an episode by id."""
    message = await episode_service.delete_episode(episode_id)
    return create_response(data=message)
