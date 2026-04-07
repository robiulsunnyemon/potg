import asyncio
from app.core.database import connect_db, disconnect_db
from app.modules.coins.service import CoinsService
from app.modules.coins.schemas import CoinPackageCreate

async def main():
    await connect_db()
    service = CoinsService()
    try:
        data = CoinPackageCreate(
            id="test_id_123",
            packageName="500_coins",
            baseCoins=500,
            bonusCoins=75,
            priceUsd=8.0
        )
        res = await service.create_package(data)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error:", str(e))
    finally:
        await disconnect_db()

if __name__ == "__main__":
    asyncio.run(main())
