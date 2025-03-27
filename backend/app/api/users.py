from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Optional
import uuid
import logging
from ..config import settings
from ..models import User, BrandAsset
from ..database import db, create_item, get_item, update_item, list_items, delete_item

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

from ..services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

# Add authentication dependency to all routes
router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/")
async def create_user(user: User):
    """
    Create a new user
    """
    logger.info(f"Creating new user: {user.email}")
    
    # Check if user with the same email already exists
    for existing_user in db.users.values():
        if existing_user.get("email") == user.email:
            raise HTTPException(
                status_code=400,
                detail=f"User with email {user.email} already exists"
            )
    
    # Create the user
    user_data = await create_item(db.users, user)
    
    logger.info(f"User created: {user_data['id']}")
    return user_data

@router.get("/{user_id}")
async def get_user(user_id: str):
    """
    Get a user by ID
    """
    logger.info(f"Getting user ID: {user_id}")
    
    user = await get_item(db.users, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User not found: {user_id}"
        )
    
    return user

@router.put("/{user_id}")
async def update_user(user_id: str, user_update: dict = Body(...)):
    """
    Update a user
    """
    logger.info(f"Updating user ID: {user_id}")
    
    # Check if user exists
    user = await get_item(db.users, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User not found: {user_id}"
        )
    
    # Update the user
    updated_user = await update_item(db.users, user_id, user_update)
    
    logger.info(f"User updated: {user_id}")
    return updated_user

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """
    Delete a user
    """
    logger.info(f"Deleting user ID: {user_id}")
    
    # Check if user exists
    user = await get_item(db.users, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User not found: {user_id}"
        )
    
    # Delete the user
    success = await delete_item(db.users, user_id)
    
    if success:
        logger.info(f"User deleted: {user_id}")
        return {"message": f"User {user_id} deleted successfully"}
    else:
        logger.error(f"Failed to delete user: {user_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user: {user_id}"
        )

@router.post("/{user_id}/brand-assets")
async def create_brand_asset(user_id: str, asset: BrandAsset):
    """
    Create a new brand asset for a user
    """
    logger.info(f"Creating brand asset for user ID: {user_id}")
    
    # Check if user exists
    user = await get_item(db.users, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User not found: {user_id}"
        )
    
    # Set the user ID for the asset
    asset.user_id = user_id
    
    # Create the asset
    asset_data = await create_item(db.brand_assets, asset)
    
    logger.info(f"Brand asset created: {asset_data['id']}")
    return asset_data

@router.get("/{user_id}/brand-assets")
async def list_brand_assets(user_id: str):
    """
    List brand assets for a user
    """
    logger.info(f"Listing brand assets for user ID: {user_id}")
    
    # Check if user exists
    user = await get_item(db.users, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User not found: {user_id}"
        )
    
    # Filter assets by user ID
    assets = []
    for asset in db.brand_assets.values():
        if asset.get("user_id") == user_id:
            assets.append(asset)
    
    return {"assets": assets}

@router.get("/{user_id}/brand-assets/{asset_id}")
async def get_brand_asset(user_id: str, asset_id: str):
    """
    Get a brand asset by ID
    """
    logger.info(f"Getting brand asset ID: {asset_id} for user ID: {user_id}")
    
    # Get the asset
    asset = await get_item(db.brand_assets, asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Brand asset not found: {asset_id}"
        )
    
    # Check if the asset belongs to the user
    if asset.get("user_id") != user_id:
        raise HTTPException(
            status_code=403,
            detail=f"Brand asset {asset_id} does not belong to user {user_id}"
        )
    
    return asset

@router.delete("/{user_id}/brand-assets/{asset_id}")
async def delete_brand_asset(user_id: str, asset_id: str):
    """
    Delete a brand asset
    """
    logger.info(f"Deleting brand asset ID: {asset_id} for user ID: {user_id}")
    
    # Get the asset
    asset = await get_item(db.brand_assets, asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Brand asset not found: {asset_id}"
        )
    
    # Check if the asset belongs to the user
    if asset.get("user_id") != user_id:
        raise HTTPException(
            status_code=403,
            detail=f"Brand asset {asset_id} does not belong to user {user_id}"
        )
    
    # Delete the asset
    success = await delete_item(db.brand_assets, asset_id)
    
    if success:
        logger.info(f"Brand asset deleted: {asset_id}")
        return {"message": f"Brand asset {asset_id} deleted successfully"}
    else:
        logger.error(f"Failed to delete brand asset: {asset_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete brand asset: {asset_id}"
        )
