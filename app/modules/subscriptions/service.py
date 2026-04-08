from app.core.database import prisma
from app.modules.subscriptions.schemas import SubscriptionPlanCreate, SubscriptionPlanUpdate, PaginatedSubscriptionPlanResponse

class SubscriptionsService:
    async def create_plan(self, data: SubscriptionPlanCreate):
        plan = await prisma.subscriptionplan.create(
            data={
                "id": data.id,
                "packageName": data.packageName,
                "planName": data.planName,
                "priceUsd": data.priceUsd,
                "duration": data.duration,
                "benefits": data.benefits,
            }
        )
        return plan

    async def get_plans(self) -> PaginatedSubscriptionPlanResponse:
        total = await prisma.subscriptionplan.count()
        plans = await prisma.subscriptionplan.find_many(
            order={"priceUsd": "asc"}
        )
        return PaginatedSubscriptionPlanResponse(
            total=total,
            plans=plans
        )

    async def update_plan(self, plan_id: str, data: SubscriptionPlanUpdate):
        update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
        if not update_data:
            return await prisma.subscriptionplan.find_unique(where={"id": plan_id})
        
        plan = await prisma.subscriptionplan.update(
            where={"id": plan_id},
            data=update_data
        )
        return plan

    async def delete_plan(self, plan_id: str):
        await prisma.subscriptionplan.delete(where={"id": plan_id})
        return "Plan deleted successfully."
