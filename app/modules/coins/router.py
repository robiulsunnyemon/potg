from fastapi import APIRouter, Depends, status
from app.modules.coins.service import CoinsService
from app.modules.coins.schemas import CoinPackageCreate, CoinPackageResponse, PaginatedCoinPackageResponse, CoinPackageUpdate
from app.common.response import ResponseSchema, create_response
from app.core.dependencies import CurrentAdminDep

router = APIRouter(prefix="/coins/packages", tags=["Coins"])
coins_service = CoinsService()

@router.post("", response_model=ResponseSchema[CoinPackageResponse], status_code=status.HTTP_201_CREATED)
async def create_coin_package(
    data: CoinPackageCreate,
    current_admin: CurrentAdminDep
):
    """[Admin Only] Create a new coin package."""
    package = await coins_service.create_package(data)
    return create_response(data=package, message="Coin package created successfully.")

@router.get("", response_model=ResponseSchema[PaginatedCoinPackageResponse])
async def get_coin_packages():
    """[Public/User] Fetch all available coin packages."""
    result = await coins_service.get_packages()
    return create_response(data=result)

@router.patch("/{package_id}", response_model=ResponseSchema[CoinPackageResponse])
async def update_coin_package(
    package_id: str,
    data: CoinPackageUpdate,
    current_admin: CurrentAdminDep
):
    """[Admin Only] Update an existing coin package."""
    package = await coins_service.update_package(package_id, data)
    return create_response(data=package, message="Coin package updated successfully.")

@router.delete("/{package_id}", response_model=ResponseSchema[str])
async def delete_coin_package(
    package_id: str,
    current_admin: CurrentAdminDep
):
    """[Admin Only] Delete a coin package."""
    message = await coins_service.delete_package(package_id)
    return create_response(data=message)
