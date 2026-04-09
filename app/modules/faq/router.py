from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.modules.faq.schemas import FaqCreate, FaqUpdate, FaqResponse
from app.modules.faq.service import FaqService
from app.core.dependencies import CurrentAdminDep
from app.common.response import ResponseSchema, create_response

router = APIRouter(prefix="/faq", tags=["FAQ"])
faq_service = FaqService()

@router.post("", response_model=ResponseSchema[FaqResponse])
async def create_faq(data: FaqCreate, current_admin: CurrentAdminDep):
    """[Admin Only] Create a new FAQ."""
    try:
        faq = await faq_service.create_faq(data)
        return create_response(data=faq, message="FAQ created successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{faq_id}", response_model=ResponseSchema[FaqResponse])
async def update_faq(faq_id: str, data: FaqUpdate, current_admin: CurrentAdminDep):
    """[Admin Only] Update an existing FAQ."""
    try:
        faq = await faq_service.update_faq(faq_id, data)
        return create_response(data=faq, message="FAQ updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{faq_id}", response_model=ResponseSchema[dict])
async def delete_faq(faq_id: str, current_admin: CurrentAdminDep):
    """[Admin Only] Delete an FAQ."""
    try:
        result = await faq_service.delete_faq(faq_id)
        return create_response(data=result, message="FAQ deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("", response_model=ResponseSchema[List[FaqResponse]])
async def get_all_faqs():
    """[Public] Get all FAQs."""
    faqs = await faq_service.get_all_faqs()
    return create_response(data=faqs)

@router.get("/{faq_id}", response_model=ResponseSchema[FaqResponse])
async def get_faq_by_id(faq_id: str):
    """[Public] Get a specific FAQ by ID."""
    try:
        faq = await faq_service.get_faq_by_id(faq_id)
        return create_response(data=faq)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
