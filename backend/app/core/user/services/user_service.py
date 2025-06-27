from typing import Any, Dict

from fastapi import HTTPException, Request
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.types.type_auth import CreateUserT
from app.core.user.model.user_model import UserModel
from app.utils.password_hash import PassHash
from app.utils.types_utils.response_types import response_message


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_user(self, user_data: CreateUserT):
        hasher =  PassHash()
        """Create a new user"""
        try:
            # Check if user with email already exists
            existing_user_query = select(UserModel).where(
                UserModel.email == user_data.get("email")
            )
            existing_user_result = await self.db.execute(existing_user_query)
            existing_user = existing_user_result.scalar_one_or_none()

            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail=response_message(
                        error="Email already exists",
                        success_status=False,
                        message="A user with this email already exists",
                    ),
                )

            # Create new user instance
            new_user = UserModel(
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                email=user_data.get("email"),
                password=hasher.hash_me(user_data.get(
                    "password"
                )),  
                user_type=user_data.get("user_type"),
            )

            # Add to database
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)

            return new_user

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Failed to create user",
                ),
            )

    async def get_user_by_id(self, user_id: str):
        """Get a user by their ID"""
        try:
            query = select(UserModel).where(UserModel.id == user_id)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=response_message(
                        error="User not found",
                        success_status=False,
                        message="User not found",
                    ),
                )

            return user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Failed to retrieve user",
                ),
            )

    async def get_user_by_email(self, email: str):
        """Get a user by their email"""
        try:
            query = select(UserModel).where(UserModel.email == email)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=response_message(
                        error="User not found",
                        success_status=False,
                        message="User not found",
                    ),
                )

            return user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Failed to retrieve user",
                ),
            )

    async def get_user(self, filters: dict):
        """Get a user by any field(s) in the UserModel"""
        try:
            # Start with base query
            query = select(UserModel)

            # Build WHERE conditions dynamically based on provided filters
            conditions = []
            for field, value in filters.items():
                if hasattr(UserModel, field):
                    conditions.append(getattr(UserModel, field) == value)
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=response_message(
                            error=f"Invalid field: {field}",
                            success_status=False,
                            message=f"Field '{field}' does not exist in UserModel",
                        ),
                    )

            # Apply all conditions
            if conditions:
                query = query.where(*conditions)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=response_message(
                        error="No filters provided",
                        success_status=False,
                        message="At least one filter must be provided",
                    ),
                )

            # Execute query
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=response_message(
                        error="User not found",
                        success_status=False,
                        message="No user found matching the provided criteria",
                    ),
                )

            return user

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Failed to retrieve user",
                ),
            )

    async def get_users(self, skip: int = 0, limit: int = 100):
        """Get a list of users with pagination"""
        try:
            query = select(UserModel).offset(skip).limit(limit)
            result = await self.db.execute(query)
            users = result.scalars().all()

            return users
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Failed to retrieve users",
                ),
            )

    async def search_users(self, search_term: str, skip: int = 0, limit: int = 100):
        """Search users by name or email"""
        try:
            query = (
                select(UserModel)
                .where(
                    UserModel.first_name.ilike(f"%{search_term}%")
                    | UserModel.last_name.ilike(f"%{search_term}%")
                    | UserModel.email.ilike(f"%{search_term}%")
                )
                .offset(skip)
                .limit(limit)
            )
            result = await self.db.execute(query)
            users = result.scalars().all()

            return users
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e), success_status=False, message="Failed to search users"
                ),
            )

    async def update_user(self, user_id: str, update_data: Dict[str, Any]):
        """Update user data"""
        try:
            # First check if user exists
            await self.get_user_by_id(user_id)

            # Remove None values and empty strings from update_data
            filtered_data = {
                k: v for k, v in update_data.items() if v is not None and v != ""
            }

            if not filtered_data:
                raise HTTPException(
                    status_code=400,
                    detail=response_message(
                        error="No valid data provided",
                        success_status=False,
                        message="No valid data provided for update",
                    ),
                )

            # Check if trying to update email to an existing one
            if "email" in filtered_data:
                existing_user_query = select(UserModel).where(
                    UserModel.email == filtered_data["email"], UserModel.id != user_id
                )
                existing_user_result = await self.db.execute(existing_user_query)
                existing_user = existing_user_result.scalar_one_or_none()

                if existing_user:
                    raise HTTPException(
                        status_code=400,
                        detail=response_message(
                            error="Email already exists",
                            success_status=False,
                            message="Another user with this email already exists",
                        ),
                    )

            # Validate fields exist in model
            valid_fields = {
                "first_name",
                "last_name",
                "email",
                "password",
                "user_type",
                "email_verified",
                "is_active",
                "is_blocked",
            }
            invalid_fields = set(filtered_data.keys()) - valid_fields
            if invalid_fields:
                raise HTTPException(
                    status_code=400,
                    detail=response_message(
                        error=f"Invalid fields: {', '.join(invalid_fields)}",
                        success_status=False,
                        message="Some fields are not valid for update",
                    ),
                )

            # Perform update
            query = (
                update(UserModel).where(UserModel.id == user_id).values(**filtered_data)
            )
            await self.db.execute(query)
            await self.db.commit()

            # Return updated user
            return await self.get_user_by_id(user_id)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Failed to update user",
                ),
            )

    async def delete_user(self, user_id: str):
        """Delete a user"""
        try:
            # First check if user exists
            user = await self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=response_message(
                        error="User not found",
                        success_status=False,
                        message="User account not found",
                    ),
                )

            # Perform soft delete by setting is_active to False
            query = (
                update(UserModel).where(UserModel.id == user_id).values(is_active=False)
            )
            await self.db.execute(query)
            await self.db.commit()

            return {"message": "User deactivated successfully", "user_id": user_id}

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Failed to delete user",
                ),
            )

    async def hard_delete_user(self, user_id: str):
        """Permanently delete a user (use with caution)"""
        try:
            # First check if user exists
            await self.get_user_by_id(user_id)

            # Perform hard delete
            query = delete(UserModel).where(UserModel.id == user_id)
            await self.db.execute(query)
            await self.db.commit()

            return {"message": "User permanently deleted", "user_id": user_id}

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Failed to permanently delete user",
                ),
            )

    async def activate_user(self, user_id: str):
        """Activate a deactivated user"""
        try:
            await self.update_user(user_id, {"is_active": True})
            return {"message": "User activated successfully", "user_id": user_id}
        except Exception as e:
            raise e

    async def block_user(self, user_id: str):
        """Block a user"""
        try:
            await self.update_user(user_id, {"is_blocked": True})
            return {"message": "User blocked successfully", "user_id": user_id}
        except Exception as e:
            raise e

    async def unblock_user(self, user_id: str):
        """Unblock a user"""
        try:
            await self.update_user(user_id, {"is_blocked": False})
            return {"message": "User unblocked successfully", "user_id": user_id}
        except Exception as e:
            raise e

    async def verify_user_email(self, user_id: str):
        """Mark user email as verified"""
        try:
            await self.update_user(user_id, {"email_verified": True})
            return {"message": "User email verified successfully", "user_id": user_id}
        except Exception as e:
            raise e

    @staticmethod
    def get_logged_in_user(request: Request):
        """Get the logged-in user from request state"""
        user_response = getattr(request.state, "user", None)

        if not user_response:
            raise HTTPException(
                status_code=401,
                detail=response_message(
                    error="User not authorized",
                    success_status=False,
                    message="User not authorized",
                ),
            )

        # Extract user data from the response structure
        if isinstance(user_response, dict) and "data" in user_response:
            return user_response["data"]

        return user_response

    async def get_current_user_profile(self, request: Request):
        """Get the current user's profile"""
        try:
            user_data = self.get_logged_in_user(request)

            # If user_data is a dict, get the ID from it
            if isinstance(user_data, dict):
                user_id = user_data.get("id")
            else:
                user_id = getattr(user_data, "id", None)

            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail=response_message(
                        error="Invalid user data",
                        success_status=False,
                        message="User not authorized",
                    ),
                )

            # Get fresh user data from database
            user = await self.get_user_by_id(user_id)
            return user

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Failed to get user profile",
                ),
            )

    async def update_current_user_profile(
        self, request: Request, update_data: Dict[str, Any]
    ):
        """Update the current user's profile"""
        try:
            user_data = self.get_logged_in_user(request)

            # If user_data is a dict, get the ID from it
            if isinstance(user_data, dict):
                user_id = user_data.get("id")
            else:
                user_id = getattr(user_data, "id", None)

            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail=response_message(
                        error="Invalid user data",
                        success_status=False,
                        message="User not authorized",
                    ),
                )

            # Remove sensitive fields that users shouldn't update themselves
            restricted_fields = {"is_active", "is_blocked", "user_type"}
            filtered_data = {
                k: v for k, v in update_data.items() if k not in restricted_fields
            }

            return await self.update_user(user_id, filtered_data)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Failed to update user profile",
                ),
            )

    async def require_authentication(self, request: Request):
        """Simple authentication check - just ensures user is logged in"""
        user_data = self.get_logged_in_user(request)

        # Return the user data for convenience
        return user_data
