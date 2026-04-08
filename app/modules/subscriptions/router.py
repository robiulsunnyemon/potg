from fastapi import APIRouter, Depends, status
from app.modules.subscriptions.service import SubscriptionsService
from app.modules.subscriptions.schemas import SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanResponse, PaginatedSubscriptionPlanResponse
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentAdminDep

router = APIRouter(prefix="/subscriptions/plans", tags=["Subscriptions"])
subscriptions_service = SubscriptionsService()

@router.post("", response_model=ResponseSchema[SubscriptionPlanResponse], status_code=status.HTTP_201_CREATED)
async def create_subscription_plan(
    data: SubscriptionPlanCreate,
    current_admin: CurrentAdminDep
):
    """[Admin Only] Create a new subscription plan."""
    plan = await subscriptions_service.create_plan(data)
    return create_response(data=plan, message="Subscription plan created successfully.")

@router.get("", response_model=ResponseSchema[PaginatedSubscriptionPlanResponse])
async def get_subscription_plans():
    """[Public/User] Fetch all available subscription plans."""
    result = await subscriptions_service.get_plans()
    return create_response(data=result)

@router.put("/{plan_id}", response_model=ResponseSchema[SubscriptionPlanResponse])
async def update_subscription_plan(
    plan_id: str,
    data: SubscriptionPlanUpdate,
    current_admin: CurrentAdminDep
):
    """[Admin Only] Update an existing subscription plan."""
    plan = await subscriptions_service.update_plan(plan_id, data)
    return create_response(data=plan, message="Subscription plan updated successfully.")

@router.delete("/{plan_id}", response_model=ResponseSchema[str])
async def delete_subscription_plan(
    plan_id: str,
    current_admin: CurrentAdminDep
):
    """[Admin Only] Delete a subscription plan."""
    message = await subscriptions_service.delete_plan(plan_id)
    return create_response(data=message)
