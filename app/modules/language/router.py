from fastapi import APIRouter, Depends, status
from app.modules.language.service import LanguageService
from app.modules.language.schemas import LanguageCreate, LanguageUpdate, LanguageResponse
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentAdminDep
from typing import List

router = APIRouter(prefix="/languages", tags=["Languages"])
language_service = LanguageService()

@router.post("", response_model=ResponseSchema[LanguageResponse], status_code=status.HTTP_201_CREATED)
async def create_language(data: LanguageCreate, admin: CurrentAdminDep):
    """[Admin Only] Create a new language."""
    language = await language_service.create_language(data)
    return create_response(language, message="Language created successfully")

@router.get("", response_model=ResponseSchema[List[LanguageResponse]])
async def get_languages():
    """Fetch all available languages."""
    languages = await language_service.get_languages()
    return create_response(languages)

@router.get("/{language_id}", response_model=ResponseSchema[LanguageResponse])
async def get_language(language_id: str):
    """Fetch details of a single language."""
    language = await language_service.get_language(language_id)
    return create_response(language)

@router.patch("/{language_id}", response_model=ResponseSchema[LanguageResponse])
async def update_language(language_id: str, data: LanguageUpdate, admin: CurrentAdminDep):
    """[Admin Only] Update an existing language."""
    language = await language_service.update_language(language_id, data)
    return create_response(language, message="Language updated successfully")

@router.delete("/{language_id}", response_model=ResponseSchema[str])
async def delete_language(language_id: str, admin: CurrentAdminDep):
    """[Admin Only] Delete a language by id."""
    message = await language_service.delete_language(language_id)
    return create_response(data=message)
