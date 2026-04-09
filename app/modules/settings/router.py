from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.modules.settings.schemas import AppPageCreate, AppPageUpdate, AppPageResponse
from app.modules.settings.service import SettingsService
from app.core.dependencies import CurrentAdminDep
from app.common.response import ResponseSchema, create_response

router = APIRouter(prefix="/settings", tags=["Settings"])
settings_service = SettingsService()

@router.post("", response_model=ResponseSchema[AppPageResponse])
async def create_page(data: AppPageCreate, current_admin: CurrentAdminDep):
    """[Admin Only] Create a new static page."""
    try:
        page = await settings_service.create_page(data)
        return create_response(data=page, message="Page created successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{page_id}", response_model=ResponseSchema[AppPageResponse])
async def update_page(page_id: str, data: AppPageUpdate, current_admin: CurrentAdminDep):
    """[Admin Only] Update an existing static page."""
    try:
        page = await settings_service.update_page(page_id, data)
        return create_response(data=page, message="Page updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{page_id}", response_model=ResponseSchema[dict])
async def delete_page(page_id: str, current_admin: CurrentAdminDep):
    """[Admin Only] Delete a static page."""
    try:
        result = await settings_service.delete_page(page_id)
        return create_response(data=result, message="Page deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("", response_model=ResponseSchema[List[AppPageResponse]])
async def get_all_pages():
    """[Public] Get a list of all static pages."""
    pages = await settings_service.get_all_pages()
    return create_response(data=pages)

@router.get("/{title}", response_model=ResponseSchema[AppPageResponse])
async def get_page_by_title(title: str):
    """[Public] Get a specific page by its title."""
    try:
        page = await settings_service.get_page_by_title(title)
        return create_response(data=page)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
