
from fastapi import APIRouter, HTTPException, Query, Response, status

from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.services import asset_service

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("", response_model=AssetResponse, status_code=201)
def create_asset(data: AssetCreate):
    try:
        return asset_service.create_asset(data.model_dump())
    except asset_service.DuplicateAssetCodeError:
        raise HTTPException(status_code=409, detail="Asset code already exists")


@router.get("", response_model=list[AssetResponse])
def list_assets(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return asset_service.get_all_assets(limit, offset)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int):
    try:
        return asset_service.get_asset(asset_id)
    except asset_service.AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, data: AssetUpdate):
    try:
        return asset_service.update_asset(
            asset_id, data.model_dump(exclude_unset=True)
        )
    except asset_service.AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except asset_service.DuplicateAssetCodeError:
        raise HTTPException(status_code=409, detail="Asset code already exists")


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int):
    try:
        asset_service.delete_asset(asset_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except asset_service.AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
