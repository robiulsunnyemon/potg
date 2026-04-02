from fastapi import APIRouter, Depends, status
from app.modules.category.service import CategoryService
from app.modules.category.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentAdminDep
from typing import List

router = APIRouter(prefix="/categories", tags=["Categories"])
category_service = CategoryService()

@router.post("", response_model=ResponseSchema[CategoryResponse], status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, admin: CurrentAdminDep):
    """[Admin Only] Create a new category."""
    category = await category_service.create_category(data)
    return create_response(category, message="Category created successfully")

@router.get("", response_model=ResponseSchema[List[CategoryResponse]])
async def get_categories():
    """Fetch all available categories."""
    categories = await category_service.get_categories()
    return create_response(categories)

@router.get("/{category_id}", response_model=ResponseSchema[CategoryResponse])
async def get_category(category_id: str):
    """Fetch details of a single category."""
    category = await category_service.get_category(category_id)
    return create_response(category)

@router.patch("/{category_id}", response_model=ResponseSchema[CategoryResponse])
async def update_category(category_id: str, data: CategoryUpdate, admin: CurrentAdminDep):
    """[Admin Only] Update an existing category."""
    category = await category_service.update_category(category_id, data)
    return create_response(category, message="Category updated successfully")

@router.delete("/{category_id}", response_model=ResponseSchema[str])
async def delete_category(category_id: str, admin: CurrentAdminDep):
    """[Admin Only] Delete a category by id."""
    message = await category_service.delete_category(category_id)
    return create_response(data=message)
