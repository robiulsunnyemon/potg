from app.core.database import prisma
from app.modules.rewards.schemas import RewardSettingsUpdate, RewardSettingSchema, RewardHistoryResponse, RewardHistorySchema
from prisma.enums import RewardDay
from datetime import datetime, timezone

DAY_ENUM_LIST = [
    RewardDay.DAY_ONE,
    RewardDay.DAY_TWO,
    RewardDay.DAY_THREE,
    RewardDay.DAY_FOUR,
    RewardDay.DAY_FIVE,
    RewardDay.DAY_SIX,
    RewardDay.DAY_SEVEN,
]

class RewardsService:
    async def get_settings(self):
        settings = await prisma.rewardsetting.find_many()
        return settings

    async def update_settings(self, data: RewardSettingsUpdate):
        for setting in data.settings:
            await prisma.rewardsetting.upsert(
                where={"day": setting.day},
                data={
                    "create": {
                        "day": setting.day,
                        "coins": setting.coins
                    },
                    "update": {
                        "coins": setting.coins
                    }
                }
            )
        return await self.get_settings()

    def _get_current_day_enum(self, user_created_at: datetime) -> RewardDay:
        now = datetime.now(timezone.utc)
        
        # Calculate days difference safely
        diff = now - user_created_at
        days_since_creation = diff.days
        if days_since_creation < 0:
            days_since_creation = 0
            
        current_cycle_index = days_since_creation % 7
        return DAY_ENUM_LIST[current_cycle_index]

    async def claim_daily_reward(self, user_id: str):
        user = await prisma.user.find_unique(where={"id": user_id})
        if not user:
            raise ValueError("User not found")

        current_day_enum = self._get_current_day_enum(user.createdAt)
        today = datetime.now(timezone.utc).date()

        # Check if already claimed TODAY
        # We need to see if there's any record in UserRewardHistory matching today's date for this user
        # Since Prisma doesn't support 'date' casting perfectly in queries, we fetch and filter in Python
        # Actually, if we just check if they claimed this specific DAY_ENUM on THIS specific exact cycle.
        # Let's simplify: A user can only claim one reward per day.
        # Wait, the user can only grab each DAY_ENUM once in their lifetime based on unique composite key [userId, day].
        # The prompt says: "এর আগে ডে অয়ানের রেওয়ার্ড না পেয়ে থাকে তাহলে সে এডমিনের সেট করা coin গুলো পাবে...". 
        # So they can only EVER get Day One once!
        
        # Check if they already have this specific reward day claimed
        existing_claim = await prisma.userrewardhistory.find_unique(
            where={
                "userId_day": {
                    "userId": user_id,
                    "day": current_day_enum
                }
            }
        )

        if existing_claim:
            raise ValueError(f"You have already claimed the reward for {current_day_enum.name}.")

        # Get settings for this day to know how many coins
        setting = await prisma.rewardsetting.find_unique(where={"day": current_day_enum})
        coins_to_award = setting.coins if setting else 0

        # Create claim history
        await prisma.userrewardhistory.create(
            data={
                "userId": user_id,
                "day": current_day_enum,
                "coinsRewarded": coins_to_award
            }
        )

        # Update user balance
        updated_user = await prisma.user.update(
            where={"id": user_id},
            data={"balance": {"increment": coins_to_award}}
        )

        return {"message": "Reward claimed successfully", "coins": coins_to_award, "new_balance": updated_user.balance}

    async def get_reward_history(self, user_id: str) -> RewardHistoryResponse:
        user = await prisma.user.find_unique(where={"id": user_id})
        if not user:
            raise ValueError("User not found")

        current_day_enum = self._get_current_day_enum(user.createdAt)
        
        # Get all claims for this user
        claims = await prisma.userrewardhistory.find_many(where={"userId": user_id})
        claims_dict = {claim.day: claim for claim in claims}
        
        history_list = []
        today_status = "Available"
        
        # Find index of current day
        current_index = DAY_ENUM_LIST.index(current_day_enum)
        
        for idx, day_enum in enumerate(DAY_ENUM_LIST):
            if day_enum in claims_dict:
                claim = claims_dict[day_enum]
                history_list.append(RewardHistorySchema(
                    day=day_enum.name,
                    status="Claimed",
                    coinsRewarded=claim.coinsRewarded,
                    claimedDate=claim.claimedDate
                ))
                if day_enum == current_day_enum:
                    today_status = "Claimed"
            else:
                # If the day index is less than current index, it's missed
                if idx < current_index:
                    status = "Missed"
                elif idx == current_index:
                    status = "Available"
                else:
                    status = "Locked"
                    
                history_list.append(RewardHistorySchema(
                    day=day_enum.name,
                    status=status,
                    coinsRewarded=0
                ))

        return RewardHistoryResponse(
            history=history_list,
            today_status=today_status,
            today_day=current_day_enum.name
        )
