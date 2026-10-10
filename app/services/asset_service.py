
import sqlite3

from app.repositories import asset_repository


class AssetNotFoundError(Exception):
    pass


class DuplicateAssetCodeError(Exception):
    pass


def create_asset(data):
    try:
        return asset_repository.create_asset(
            data["asset_code"],
            data["name"],
            data["category"],
        )
    except sqlite3.IntegrityError as exc:
        if "asset_code" in str(exc):
            raise DuplicateAssetCodeError from exc
        raise


def get_all_assets(limit=20, offset=0):
    return asset_repository.get_all_assets(limit, offset)


def get_asset(asset_id):
    asset = asset_repository.get_asset_by_id(asset_id)
    if asset is None:
        raise AssetNotFoundError
    return asset


def update_asset(asset_id, data):
    get_asset(asset_id)

    cleaned_data = {
        key: value.strip()
        for key, value in data.items()
        if value is not None
    }

    try:
        return asset_repository.update_asset(asset_id, cleaned_data)
    except sqlite3.IntegrityError as exc:
        if "asset_code" in str(exc):
            raise DuplicateAssetCodeError from exc
        raise


def delete_asset(asset_id):
    get_asset(asset_id)
    return asset_repository.delete_asset(asset_id)
