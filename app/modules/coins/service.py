from app.core.database import prisma
from app.modules.coins.schemas import CoinPackageCreate, PaginatedCoinPackageResponse, CoinPackageUpdate

class CoinsService:
    async def create_package(self, data: CoinPackageCreate):
        # Create coin package
        package = await prisma.coinpackage.create(
            data={
                "id": data.id,
                "packageName": data.packageName,
                "baseCoins": data.baseCoins,
                "bonusCoins": data.bonusCoins,
                "priceUsd": data.priceUsd,
            }
        )
        return package

    async def get_packages(self) -> PaginatedCoinPackageResponse:
        total = await prisma.coinpackage.count()
        packages = await prisma.coinpackage.find_many(
            order={"baseCoins": "asc"}
        )
        return PaginatedCoinPackageResponse(
            total=total,
            packages=packages
        )

    async def update_package(self, package_id: str, data: CoinPackageUpdate):
        # Update coin package
        update_data = data.model_dump(exclude_unset=True)
        package = await prisma.coinpackage.update(
            where={"id": package_id},
            data=update_data
        )
        return package

    async def delete_package(self, package_id: str):
        await prisma.coinpackage.delete(where={"id": package_id})
        return "Package deleted successfully."
