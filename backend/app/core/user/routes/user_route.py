from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database.db import get_db
from app.core.user.services.user_service import UserService
from app.utils.types_utils.response_types import response_message

# Remove unused Pydantic models since we're using Dict[str, Any] responses
# Keep only the request models

class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    user_type: Optional[str] = None

class UserProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


# Router
user_router = APIRouter()


@user_router.get("/me")
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current authenticated user's profile
    
    Requires valid access token in Authorization header
    """
    user_service = UserService(db)
    try:
        user = await user_service.get_current_user_profile(request)
        
        # Remove password from response
        user_dict = user.__dict__.copy() if hasattr(user, "__dict__") else {}
        user_dict.pop("password", None)
        user_dict.pop("_sa_instance_state", None)  # Remove SQLAlchemy state
        
        return {
            "success": True,
            "message": "User profile retrieved successfully",
            "data": user_dict
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Failed to retrieve user profile",
                success_status=False,
                message="An error occurred while retrieving user profile",
            ),
        )


@user_router.put("/me")
async def update_current_user(
    request: Request,
    user_data: UserProfileUpdateRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update current authenticated user's profile
    
    Requires valid access token in Authorization header
    """
    user_service = UserService(db)
    try:
        # Convert to dict and remove None values
        update_data = user_data.model_dump(exclude_unset=True)
        
        user = await user_service.update_current_user_profile(request, update_data)
        
        # Remove password from response
        user_dict = user.__dict__.copy() if hasattr(user, "__dict__") else {}
        user_dict.pop("password", None)
        user_dict.pop("_sa_instance_state", None)  # Remove SQLAlchemy state
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": user_dict
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Failed to update user profile",
                success_status=False,
                message="An error occurred while updating user profile",
            ),
        )


@user_router.get("/")
async def get_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get list of users with pagination (Admin only)
    
    Requires valid access token in Authorization header
    """
    user_service = UserService(db)
    try:
        # Check authentication
        await user_service.require_authentication(request)
        
        users = await user_service.get_users(skip=skip, limit=limit)
        
        # Remove passwords from all users
        users_data = []
        for user in users:
            user_dict = user.__dict__.copy() if hasattr(user, "__dict__") else {}
            user_dict.pop("password", None)
            user_dict.pop("_sa_instance_state", None)
            users_data.append(user_dict)
        
        return {
            "success": True,
            "message": "Users retrieved successfully",
            "data": {
                "users": users_data,
                "total": len(users_data),
                "skip": skip,
                "limit": limit
            }
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Failed to retrieve users",
                success_status=False,
                message="An error occurred while retrieving users",
            ),
        )


@user_router.get("/search")
async def search_users(
    request: Request,
    q: str = Query(..., min_length=1, description="Search term"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Search users by name or email (Admin only)
    
    Requires valid access token in Authorization header
    """
    user_service = UserService(db)
    try:
        # Check authentication
        await user_service.require_authentication(request)
        
        users = await user_service.search_users(q, skip=skip, limit=limit)
        
        # Remove passwords from all users
        users_data = []
        for user in users:
            user_dict = user.__dict__.copy() if hasattr(user, "__dict__") else {}
            user_dict.pop("password", None)
            user_dict.pop("_sa_instance_state", None)
            users_data.append(user_dict)
        
        return {
            "success": True,
            "message": "Users search completed successfully",
            "data": {
                "users": users_data,
                "total": len(users_data),
                "skip": skip,
                "limit": limit,
                "search_term": q
            }
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Failed to search users",
                success_status=False,
                message="An error occurred while searching users",
            ),
        )


@user_router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user by ID (Admin only)
    
    Requires valid access token in Authorization header
    """
    user_service = UserService(db)
    try:
        # Check authentication
        await user_service.require_authentication(request)
        
        user = await user_service.get_user_by_id(user_id)
        
        # Remove password from response
        user_dict = user.__dict__.copy() if hasattr(user, "__dict__") else {}
        user_dict.pop("password", None)
        user_dict.pop("_sa_instance_state", None)  # Remove SQLAlchemy state
        
        return {
            "success": True,
            "message": "User retrieved successfully",
            "data": user_dict
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Failed to retrieve user",
                success_status=False,
                message="An error occurred while retrieving user",
            ),
        )


@user_router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update user by ID (Admin only)
    
    Requires valid access token in Authorization header
    """
    user_service = UserService(db)
    try:
        # Check authentication
        await user_service.require_authentication(request)
        
        # Convert to dict and remove None values
        update_data = user_data.model_dump(exclude_unset=True)
        
        user = await user_service.update_user(user_id, update_data)
        
        # Remove password from response
        user_dict = user.__dict__.copy() if hasattr(user, "__dict__") else {}
        user_dict.pop("password", None)
        user_dict.pop("_sa_instance_state", None)  # Remove SQLAlchemy state
        
        return {
            "success": True,
            "message": "User updated successfully",
            "data": user_dict
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Failed to update user",
                success_status=False,
                message="An error occurred while updating user",
            ),
        )


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    hard_delete: bool = Query(False, description="Permanently delete user"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete user by ID (Admin only)
    
    Requires valid access token in Authorization header
    """
    user_service = UserService(db)
    try:
        # Check authentication
        await user_service.require_authentication(request)
        
        if hard_delete:
            result = await user_service.hard_delete_user(user_id)
        else:
            result = await user_service.delete_user(user_id)
        
        return {
            "success": True,
            "message": result["message"],
            "data": result
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Failed to delete user",
                success_status=False,
                message="An error occurred while deleting user",
            ),
        )


@user_router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Activate a deactivated user (Admin only)"""
    user_service = UserService(db)
    
    # Check authentication
    await user_service.require_authentication(request)
    
    result = await user_service.activate_user(user_id)
    
    return response_message(
        data=result,
        success_status=True,
        message=result["message"]
    )


@user_router.post("/{user_id}/block")
async def block_user(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Block a user (Admin only)"""
    user_service = UserService(db)
    
    # Check authentication
    await user_service.require_authentication(request)
    
    result = await user_service.block_user(user_id)
    
    return response_message(
        data=result,
        success_status=True,
        message=result["message"]
    )


@user_router.post("/{user_id}/unblock")
async def unblock_user(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Unblock a user (Admin only)"""
    user_service = UserService(db)
    
    # Check authentication
    await user_service.require_authentication(request)
    
    result = await user_service.unblock_user(user_id)
    
    return response_message(
        data=result,
        success_status=True,
        message=result["message"]
    )


@user_router.post("/{user_id}/verify-email")
async def verify_user_email(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Verify user email (Admin only)"""
    user_service = UserService(db)
    
    # Check authentication
    await user_service.require_authentication(request)
    
    result = await user_service.verify_user_email(user_id)
    
    return response_message(
        data=result,
        success_status=True,
        message=result["message"]
    )