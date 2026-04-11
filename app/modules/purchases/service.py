from app.core.database import prisma
from app.core.config import settings
from app.modules.purchases.schemas import PurchaseVerificationRequest
from app.common.exceptions import BadRequestException, NotFoundException
import json
import os

class PurchasesService:
    async def verify_google_purchase(self, user_id: str, data: PurchaseVerificationRequest):
        # 1. Check if mock payment is enabled
        if settings.ENABLE_MOCK_PAYMENT:
            return await self._process_mock_purchase(user_id, data, "GOOGLE_PLAY")

        # 2. Real verification logic
        # In a real scenario, you would use google-api-python-client here
        # For now, we provide the structure that can be finished with credentials
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            if not settings.GOOGLE_SERVICE_ACCOUNT_JSON or not os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_JSON):
                raise BadRequestException("Google Service Account JSON not configured correctly.")

            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT_JSON,
                scopes=['https://www.googleapis.com/auth/androidpublisher']
            )
            service = build('androidpublisher', 'v3', credentials=credentials)

            # productId in Google Play terms is the SKU
            purchase = service.purchases().products().get(
                packageName=data.packageName or settings.GOOGLE_PACKAGE_NAME,
                productId=data.productId,
                token=data.purchaseToken
            ).execute()

            # purchaseState: 0 = purchased, 1 = canceled, 2 = pending
            if purchase.get('purchaseState') == 0:
                order_id = purchase.get('orderId')
                return await self._finalize_purchase(user_id, data.productId, order_id, "GOOGLE_PLAY")
            else:
                raise BadRequestException("Purchase is not in a valid state.")

        except Exception as e:
            if isinstance(e, BadRequestException): raise e
            raise BadRequestException(f"Google Purchase Verification Failed: {str(e)}")

    async def verify_apple_purchase(self, user_id: str, data: PurchaseVerificationRequest):
        # Apple verification usually involves sending the receipt to Apple's verifyReceipt endpoint
        if settings.ENABLE_MOCK_PAYMENT:
            return await self._process_mock_purchase(user_id, data, "APPLE_STORE")

        # Real Apple logic would go here
        raise BadRequestException("Apple Purchase Verification not yet implemented for production.")

    async def _process_mock_purchase(self, user_id: str, data: PurchaseVerificationRequest, gateway: str):
        # Generate a mock order ID
        mock_order_id = f"MOCK-{gateway}-{data.purchaseToken[:8]}"
        return await self._finalize_purchase(user_id, data.productId, mock_order_id, gateway)

    async def _finalize_purchase(self, user_id: str, product_id: str, order_id: str, gateway: str):
        # 1. Check if order was already processed
        existing = await prisma.transaction.find_unique(where={"externalOrderId": order_id})
        if existing:
            raise BadRequestException("This purchase has already been processed.")

        # 2. Check if it's a Coin Package
        package = await prisma.coinpackage.find_unique(where={"id": product_id})
        
        if package:
            total_coins = package.baseCoins + package.bonusCoins
            async with prisma.tx() as tx:
                user = await tx.user.update(
                    where={"id": user_id},
                    data={"balance": {"increment": total_coins}}
                )
                from prisma.enums import TransactionType
                await tx.transaction.create(
                    data={
                        "userId": user_id,
                        "amount": total_coins,
                        "transactionType": TransactionType.PURCHASE,
                        "description": f"Purchased {package.packageName}",
                        "externalOrderId": order_id,
                        "gateway": gateway,
                        "status": "SUCCESS"
                    }
                )
            return {
                "success": True,
                "message": f"Successfully added {total_coins} coins to your account.",
                "newBalance": user.balance,
                "orderId": order_id
            }

        # 3. Check if it's a Subscription Plan
        plan = await prisma.subscriptionplan.find_unique(where={"id": product_id})
        if plan:
            from datetime import datetime, timedelta, timezone
            now = datetime.now(timezone.utc)
            
            # Calculate expiry date
            if plan.duration == "WEEKLY":
                expiry_date = now + timedelta(days=7)
            elif plan.duration == "MONTHLY":
                expiry_date = now + timedelta(days=30)
            elif plan.duration == "YEARLY":
                expiry_date = now + timedelta(days=365)
            else:
                expiry_date = now + timedelta(days=30) # Default to 30 days
                
            async with prisma.tx() as tx:
                user = await tx.user.update(
                    where={"id": user_id},
                    data={
                        "isPremium": True,
                        "premiumUntil": expiry_date
                    }
                )
                from prisma.enums import TransactionType
                await tx.transaction.create(
                    data={
                        "userId": user_id,
                        "amount": 0, # Or record price if needed
                        "transactionType": TransactionType.PURCHASE,
                        "description": f"Subscribed to {plan.planName} (Expires: {expiry_date.strftime('%Y-%m-%d')})",
                        "externalOrderId": order_id,
                        "gateway": gateway,
                        "status": "SUCCESS"
                    }
                )
            return {
                "success": True,
                "message": f"Successfully activated {plan.planName} subscription.",
                "isPremium": user.isPremium,
                "premiumUntil": user.premiumUntil,
                "orderId": order_id
            }

        raise NotFoundException("Product ID not found in Coin Packages or Subscription Plans.")

    async def handle_google_webhook(self, notification_data: dict):
        # 1. Parse the Pub/Sub message (it's base64 encoded data)
        # Note: In a real implementation, you'd decode and parse the inner JSON
        # For this logic, we assume the notification_data is already the decoded notification object
        
        sub_notification = notification_data.get("subscriptionNotification")
        if not sub_notification:
            return {"status": "ignored"}

        notification_type = sub_notification.get("notificationType")
        purchase_token = sub_notification.get("purchaseToken")

        # Notification Types:
        # 1: RECOVERED, 2: RENEWED, 3: CANCELED, 13: EXPIRED
        
        if notification_type in [1, 2]: # Recovered or Renewed
            # Extend subscription
            # In real logic, you'd fetch the latest purchase info from Google API using the token
            await self._extend_subscription_by_token(purchase_token)
        elif notification_type == 13: # Expired
            # Revoke premium
            await self._revoke_premium_by_token(purchase_token)
        
        return {"status": "processed"}

    async def _extend_subscription_by_token(self, token: str):
        # Find the transaction/user associated with this token and update premiumUntil
        transaction = await prisma.transaction.find_first(where={"externalOrderId": {"contains": token}}) # Simplified lookup
        if transaction:
            # Add another month (logic similar to _finalize_purchase)
            from datetime import datetime, timedelta, timezone
            new_expiry = datetime.now(timezone.utc) + timedelta(days=30)
            await prisma.user.update(
                where={"id": transaction.userId},
                data={"isPremium": True, "premiumUntil": new_expiry}
            )

    async def _revoke_premium_by_token(self, token: str):
        transaction = await prisma.transaction.find_first(where={"externalOrderId": {"contains": token}})
        if transaction:
            await prisma.user.update(
                where={"id": transaction.userId},
                data={"isPremium": False, "premiumUntil": None}
            )
