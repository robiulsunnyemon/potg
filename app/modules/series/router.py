from fastapi import APIRouter, Depends, Query, status, File, UploadFile
from app.modules.series.service import SeriesService
from app.modules.series.schemas import SeriesCreate, SeriesUpdate, SeriesResponse, PaginatedSeriesResponse
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentAdminDep
from typing import List, Optional

router = APIRouter(prefix="/series", tags=["Series"])
series_service = SeriesService()

@router.post("", response_model=ResponseSchema[SeriesResponse], status_code=status.HTTP_201_CREATED)
async def create_series(data: SeriesCreate, admin: CurrentAdminDep):
    """[Admin Only] Create a new series."""
    series = await series_service.create_series(data)
    return create_response(data=series, message="Series created successfully")

@router.get("", response_model=ResponseSchema[PaginatedSeriesResponse])
async def list_series(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """Fetch all series with pagination and sorting."""
    series_data = await series_service.get_series_list(page, size)
    return create_response(data=series_data)

@router.get("/{series_id}", response_model=ResponseSchema[SeriesResponse])
async def get_series(series_id: str):
    """Fetch details of a single series."""
    series = await series_service.get_series(series_id)
    return create_response(data=series)

@router.patch("/{series_id}", response_model=ResponseSchema[SeriesResponse])
async def update_series(series_id: str, data: SeriesUpdate, admin: CurrentAdminDep):
    """[Admin Only] Update an existing series."""
    series = await series_service.update_series(series_id, data)
    return create_response(data=series, message="Series updated successfully")

@router.post("/{series_id}/thumbnail", response_model=ResponseSchema[str])
async def upload_thumbnail(
    series_id: str,
    admin: CurrentAdminDep,
    file: UploadFile = File(...)
):
    """[Admin Only] Upload and update series thumbnail."""
    if not file.content_type.startswith("image/"):
        from app.common.exceptions import BadRequestException
        raise BadRequestException("File provided is not an image.")
    
    file_content = await file.read()
    image_url = await series_service.upload_thumbnail(series_id, file_content, file.filename)
    return create_response(data=image_url, message="Series thumbnail uploaded successfully")

@router.delete("/{series_id}", response_model=ResponseSchema[str])
async def delete_series(series_id: str, admin: CurrentAdminDep):
    """[Admin Only] Delete a series by id."""
    message = await series_service.delete_series(series_id)
    return create_response(data=message)
