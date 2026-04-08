from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.rewards.service import RewardsService
from app.modules.rewards.schemas import RewardSettingsUpdate, RewardSettingSchema, RewardHistoryResponse
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentAdminDep, CurrentUserDep

router = APIRouter(prefix="/rewards", tags=["Rewards"])
rewards_service = RewardsService()

@router.get("/admin/settings", response_model=ResponseSchema[list[RewardSettingSchema]])
async def get_reward_settings(current_admin: CurrentAdminDep):
    """[Admin Only] Fetch global reward settings."""
    settings = await rewards_service.get_settings()
    return create_response(data=settings)

@router.put("/admin/settings", response_model=ResponseSchema[list[RewardSettingSchema]])
async def update_reward_settings(
    data: RewardSettingsUpdate,
    current_admin: CurrentAdminDep
):
    """[Admin Only] Update global reward settings."""
    settings = await rewards_service.update_settings(data)
    return create_response(data=settings, message="Settings updated successfully.")

@router.post("/claim", response_model=ResponseSchema[dict])
async def claim_daily_reward(current_user: CurrentUserDep):
    """[User] Claim today's available reward."""
    try:
        result = await rewards_service.claim_daily_reward(current_user.id)
        return create_response(data=result, message=result["message"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history", response_model=ResponseSchema[RewardHistoryResponse])
async def get_reward_history(current_user: CurrentUserDep):
    """[User] Get status of all 7 days reward cycle."""
    try:
        history = await rewards_service.get_reward_history(current_user.id)
        return create_response(data=history)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
